import datetime
from typing import Dict, List, Any, Optional

class ContextBuilder:
    """
    Transforms raw Notion data into structured Markdown context for AI models.
    """

    @staticmethod
    def _safe_get_text(prop: Dict) -> str:
        """Safely extract text from a Notion property."""
        try:
            if prop["type"] == "title":
                return prop["title"][0]["plain_text"] if prop["title"] else ""
            if prop["type"] == "rich_text":
                return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
            if prop["type"] == "select":
                return prop["select"]["name"] if prop["select"] else ""
            if prop["type"] == "multi_select":
                return ", ".join([opt["name"] for opt in prop["multi_select"]])
            if prop["type"] == "number":
                return str(prop["number"]) if prop["number"] is not None else "0"
            if prop["type"] == "date":
                return prop["date"]["start"] if prop["date"] else ""
            if prop["type"] == "formula":
                formula_data = prop.get("formula", {})
                f_type = formula_data.get("type")
                if f_type:
                    return str(formula_data.get(f_type, ""))
            return ""
        except (KeyError, IndexError):
            return ""

    def build_daily_context(
        self, 
        pillars: List[Dict], 
        goals: List[Dict], 
        habits: List[Dict], 
        recent_journals: List[Dict],
        tasks: List[Dict]
    ) -> str:
        """
        Builds the daily context string.
        """
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        
        context = [f"# Hayat Bağlamın ({date_str} itibarıyla)\n"]

        # 1. Pillars
        context.append("## Aktif Sütunlar")
        if pillars:
            for p in pillars:
                name = self._safe_get_text(p["properties"]["Ad"])
                group = self._safe_get_text(p["properties"]["Grup"])
                context.append(f"- **{name}** ({group})")
        else:
            context.append("- Henüz aktif sütun tanımlanmamış.")
        context.append("")

        # 2. Goals
        context.append("## Mevcut Hedefler")
        if goals:
            # Group by period type if needed, but for now just list
            for g in goals:
                name = self._safe_get_text(g["properties"]["Ad"])
                p_type = self._safe_get_text(g["properties"]["Dönem Tipi"])
                progress = g["properties"].get("İlerleme", {}).get("formula", {}).get("number", 0)
                if progress is None: progress = 0
                context.append(f"- [{p_type}] {name} (İlerleme: %{int(progress * 100)})")
        else:
            context.append("- Bu dönem için aktif hedef bulunmuyor.")
        context.append("")

        # 3. Habits
        context.append("## Aktif Alışkanlıklar")
        if habits:
            for h in habits:
                name = self._safe_get_text(h["properties"]["Ad"])
                freq = self._safe_get_text(h["properties"]["Frekans"])
                last_done = self._safe_get_text(h["properties"]["Son Tamamlama"])
                context.append(f"- {name} ({freq}) [Son: {last_done if last_done else 'Hiç'}]")
        else:
            context.append("- Aktif alışkanlık bulunmuyor.")
        context.append("")

        # 4. Tasks (Actions)
        context.append("## Bugünkü Görevler")
        if tasks:
            for t in tasks:
                name = self._safe_get_text(t["properties"]["Ad"])
                priority = self._safe_get_text(t["properties"]["Öncelik"])
                context.append(f"- [{priority}] {name}")
        else:
            context.append("- Bugün için planlanmış görev yok.")
        context.append("")

        # 5. Recent Journals (Reflections)
        context.append("## Son Günlerdeki Yansımalar")
        if recent_journals:
            # Show last 3-5 entries
            for j in recent_journals[:5]:
                date = self._safe_get_text(j["properties"]["Tarih Kodu"])
                content = j.get("content", "")
                
                context.append(f"### {date}")
                if content:
                    context.append(content)
                else:
                    context.append("*İçerik bulunamadı.*")
                context.append("")
        else:
            context.append("- Yakın zamanda kaydedilmiş günce bulunmuyor.")
        context.append("")
        
        context.append("---\n*Bu bağlam Notion üzerinden otomatik olarak oluşturulmuştur.*")
        
        return "\n".join(context)

    def build_review_context(self, review_type: str, period: str, goals: List[Dict], journals: List[Dict]) -> str:
        """
        Builds strategic review context in Turkish.
        """
        context = [f"# {period} {review_type.capitalize()} Değerlendirme Bağlamı\n"]
        
        # 1. Goals for the period
        context.append(f"## {period} Dönemi Hedefleri")
        if goals:
            for g in goals:
                name = self._safe_get_text(g["properties"]["Ad"])
                status = self._safe_get_text(g["properties"]["Durum"])
                progress = g["properties"].get("İlerleme", {}).get("formula", {}).get("number", 0)
                if progress is None: progress = 0
                context.append(f"- {name} (Durum: {status}, İlerleme: %{int(progress * 100)})")
        else:
            context.append("- Bu dönem için kayıtlı hedef bulunamadı.")
        context.append("")

        # 2. Journal Summaries
        context.append(f"## {period} Dönemi Günlük Yansımaları")
        if journals:
            for j in journals:
                date = self._safe_get_text(j["properties"]["Tarih Kodu"])
                content = j.get("content", "")
                
                context.append(f"### {date}")
                if content:
                    context.append(content)
                else:
                    context.append("*İçerik bulunamadı.*")
                context.append("")
        else:
            context.append("- Bu dönemde kaydedilmiş günce bulunamadı.")
        context.append("")

        context.append("---\n*Analiz için bu verileri kullanabilirsin. Başarılar, zorluklar ve gelecek planları üzerine odaklan.*")
        
        return "\n".join(context)
