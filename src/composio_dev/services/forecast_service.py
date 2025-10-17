import os
from groq import Groq
from typing import List, Dict
from datetime import datetime, timedelta
import json
from models import InventoryItem, ForecastResult, PriorityLevel

class ForecastService:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def forecast_depletion(self, items: List[InventoryItem], forecast_days: int = 30) -> List[ForecastResult]:
        forecasts = []
        
        for item in items:
            try:
                prompt = f"""
                Analyze inventory for: {item.name}
                Current stock: {item.current_stock}
                Daily usage: {item.daily_usage}
                Min threshold: {item.min_threshold}
                
                Calculate days until depletion and provide risk factors.
                Return JSON: {{"days_until_depletion": number, "confidence_score": number, "risk_factors": ["factor1"]}}
                """
                
                response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=1024
                )
                
                llm_result = self._parse_llm_response(response.choices[0].message.content)
                fallback = self._calculate_basic_forecast(item)
                forecast = self._create_forecast_result(item, llm_result, fallback)
                forecasts.append(forecast)
                
            except Exception:
                forecast = self._create_forecast_result(item, None, self._calculate_basic_forecast(item))
                forecasts.append(forecast)
        
        return forecasts
    
    def _parse_llm_response(self, response: str) -> Dict:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
        except:
            pass
        return {}
    
    def _calculate_basic_forecast(self, item: InventoryItem) -> Dict:
        if item.daily_usage <= 0:
            days_until_depletion = 999
        else:
            days_until_depletion = max(1, (item.current_stock - item.min_threshold) / item.daily_usage)
        
        priority = "High" if days_until_depletion <= 7 else "Medium" if days_until_depletion <= 14 else "Low"
        
        return {
            "days_until_depletion": int(days_until_depletion),
            "confidence_score": 0.8,
            "risk_factors": ["Standard consumption pattern"],
            "priority_recommendation": priority
        }
    
    def _create_forecast_result(self, item: InventoryItem, llm_result: Dict, fallback: Dict) -> ForecastResult:
        result_data = llm_result if llm_result else fallback
        days_until = result_data.get("days_until_depletion", fallback["days_until_depletion"])
        depletion_date = datetime.now() + timedelta(days=days_until)
        
        return ForecastResult(
            item_id=item.item_id,
            item_name=item.name,
            current_stock=item.current_stock,
            predicted_depletion_date=depletion_date.strftime("%Y-%m-%d"),
            days_until_depletion=days_until,
            confidence_score=result_data.get("confidence_score", 0.8),
            risk_factors=result_data.get("risk_factors", ["Standard forecast"])
        )
    
    def calculate_reorder_quantity(self, item: InventoryItem, lead_time_days: int = 7, safety_days: int = 14) -> int:
        daily_usage = max(item.daily_usage, 1)
        safety_stock = daily_usage * safety_days
        order_quantity = int((daily_usage * 30) + safety_stock)
        return max(order_quantity, item.min_threshold * 2)