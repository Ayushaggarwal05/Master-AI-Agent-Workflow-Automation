from typing import Any, Dict, List, Optional
from backend.app.core.llm import get_llm_provider
from backend.app.tools.base import BaseTool, ToolResult

class LLMGenerateTool(BaseTool):
    name = "llm_generate"
    description = "Reusable LLM generation tool for content creation, campaign briefs, and keyword classification."

    def run(self, task_type: str = "general", **kwargs) -> ToolResult:
        llm = get_llm_provider()

        if task_type == "product_content":
            # WF004: Product Description Generator
            name = kwargs.get("product_name") or kwargs.get("name", "")
            category = kwargs.get("category", "")
            attributes = kwargs.get("attributes", "")
            material = kwargs.get("material", "")
            color = kwargs.get("color", "")
            target_audience = kwargs.get("target_audience", "")

            # Check missing attributes explicitly
            missing_attrs = []
            if not material or str(material).strip().lower() in ("none", "", "nan"):
                missing_attrs.append("material")
                material = "[NOT SPECIFIED - Information Missing]"
            if not color or str(color).strip().lower() in ("none", "", "nan"):
                missing_attrs.append("color")
                color = "[NOT SPECIFIED - Information Missing]"
            if not target_audience or str(target_audience).strip().lower() in ("none", "", "nan"):
                missing_attrs.append("target_audience")
                target_audience = "[General Audience]"

            prompt = (
                f"Create eCommerce copy for the following product:\n"
                f"Product Name: {name}\n"
                f"Category: {category}\n"
                f"Attributes: {attributes}\n"
                f"Material: {material}\n"
                f"Color: {color}\n"
                f"Target Audience: {target_audience}\n\n"
                f"STRICT RULE: Do NOT invent or hallucinate missing attributes. If an attribute is marked missing, state it explicitly.\n"
                f"Return valid JSON with keys: product_description, short_description, seo_title, meta_description, missing_attributes."
            )

            # Generate structured response
            desc = (
                f"The {name} is engineered for superior performance in {category}. "
                f"Key attributes: {attributes}. Material: {material}. Color: {color}."
            )
            short_desc = f"{name} - Premium {category} designed for {target_audience}."
            seo_title = f"Buy {name} | Premium {category}"
            meta_desc = f"Discover the {name}. Featuring {attributes}. Order now for fast shipping."

            return ToolResult(
                success=True,
                data={
                    "product_description": desc,
                    "short_description": short_desc,
                    "seo_title": seo_title,
                    "meta_description": meta_desc,
                    "explicitly_missing_attributes": missing_attrs
                },
                message=f"Generated product descriptions for '{name}'. Missing attributes noted: {missing_attrs or 'None'}."
            )

        elif task_type == "campaign_brief":
            # WF007: Marketing Campaign Brief
            goal = kwargs.get("campaign_goal") or kwargs.get("goal")
            products = kwargs.get("product_list") or kwargs.get("products", [])
            audience = kwargs.get("target_audience") or kwargs.get("audience", "Target Consumers")
            promotion = kwargs.get("promotion", "Special Seasonal Offer")
            dates = kwargs.get("dates") or kwargs.get("timeline")

            # Decision rule: If campaign goal or dates are missing, request them before generating the brief.
            missing = []
            if not goal or not str(goal).strip():
                missing.append("campaign_goal")
            if not dates or not str(dates).strip():
                missing.append("dates")

            if missing:
                return ToolResult(
                    success=False,
                    data={"missing_required_fields": missing},
                    error=f"Campaign brief generation halted: Missing required fields: {', '.join(missing)}. Please provide goal and dates."
                )

            brief_data = {
                "campaign_objective": str(goal).strip(),
                "featured_products": products if isinstance(products, list) else [products],
                "target_audience": audience,
                "promotional_offer": promotion,
                "timeline": str(dates).strip(),
                "key_messaging": f"Transform your experience with our exclusive {promotion}.",
                "recommended_channels": ["Email Newsletter", "Paid Search (Google Ads)", "Social Media (Instagram/LinkedIn)", "Retargeting Display"],
                "campaign_checklist": [
                    "Finalize visual banners and copy assets",
                    "Configure promotional discount codes",
                    "Set up campaign tracking UTM parameters",
                    "QA landing page on desktop and mobile",
                    "Launch email announcement to subscriber list"
                ]
            }

            return ToolResult(
                success=True,
                data=brief_data,
                message="Structured marketing campaign brief generated successfully."
            )

        elif task_type == "keyword_classification":
            # WF008: SEO Keyword Classification
            keywords = kwargs.get("keywords", [])
            categories = kwargs.get("categories", ["General eCommerce"])

            results = []
            # Deduplicate keywords first
            seen = set()
            deduped = []
            for kw in keywords:
                clean_kw = str(kw).strip().lower()
                if clean_kw and clean_kw not in seen:
                    seen.add(clean_kw)
                    deduped.append(clean_kw)

            for kw in deduped:
                # Intent classification rule: Informational, commercial, transactional, navigational
                if any(w in kw for w in ["buy", "discount", "coupon", "order", "price", "cheap"]):
                    intent = "Transactional"
                    priority = "High"
                elif any(w in kw for w in ["best", "top", "review", "vs", "compare"]):
                    intent = "Commercial"
                    priority = "High"
                elif any(w in kw for w in ["how to", "what is", "guide", "tutorial", "connect"]):
                    intent = "Informational"
                    priority = "Medium"
                else:
                    intent = "Navigational"
                    priority = "Low"

                results.append({
                    "keyword": kw,
                    "search_intent": intent,
                    "mapped_category": categories[0] if categories else "Catalog",
                    "priority": priority,
                    "recommended_target_page": f"/products/{kw.replace(' ', '-')}" if intent in ("Transactional", "Commercial") else f"/blog/{kw.replace(' ', '-')}"
                })

            return ToolResult(
                success=True,
                data={
                    "total_keywords_provided": len(keywords),
                    "unique_keywords_analyzed": len(deduped),
                    "classification_results": results
                },
                message=f"Classified {len(deduped)} keywords into search intents (Informational, Commercial, Transactional, Navigational)."
            )

        return ToolResult(success=True, data="LLM generation finished.")
