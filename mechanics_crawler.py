from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List, Dict
import asyncio
import json
import os

class MechanicDetail(BaseModel):
    name: str = Field(..., description="Nama mechanic")
    description: str = Field(..., description="Penjelasan detail tentang mechanic")
    sub_mechanics: List[Dict] = Field(default=[], description="Sub-mechanics jika ada")

class DotaMechanics(BaseModel):
    unit_mechanics: List[MechanicDetail] = Field(..., description="Mechanics terkait unit/hero")
    attack_mechanics: List[MechanicDetail] = Field(..., description="Mechanics terkait serangan")
    world_mechanics: List[MechanicDetail] = Field(..., description="Mechanics terkait world/map")
    status_effects: List[MechanicDetail] = Field(..., description="Mechanics terkait status effect")
    gameplay_mechanics: List[MechanicDetail] = Field(..., description="Mechanics terkait gameplay")

def convert_to_markdown(mechanics_data: DotaMechanics) -> str:
    markdown = "# Dota 2 Game Mechanics\n\n"
    
    # Unit Mechanics
    markdown += "## Unit Mechanics\n\n"
    for mech in mechanics_data.unit_mechanics:
        markdown += f"### {mech.name}\n"
        markdown += f"{mech.description}\n\n"
        if mech.sub_mechanics:
            for sub in mech.sub_mechanics:
                markdown += f"- **{sub['name']}**: {sub['description']}\n"
            markdown += "\n"
    
    # Attack Mechanics
    markdown += "## Attack Mechanics\n\n"
    for mech in mechanics_data.attack_mechanics:
        markdown += f"### {mech.name}\n"
        markdown += f"{mech.description}\n\n"
        if mech.sub_mechanics:
            for sub in mech.sub_mechanics:
                markdown += f"- **{sub['name']}**: {sub['description']}\n"
            markdown += "\n"
            
    # World Mechanics
    markdown += "## World Mechanics\n\n"
    for mech in mechanics_data.world_mechanics:
        markdown += f"### {mech.name}\n"
        markdown += f"{mech.description}\n\n"
        if mech.sub_mechanics:
            for sub in mech.sub_mechanics:
                markdown += f"- **{sub['name']}**: {sub['description']}\n"
            markdown += "\n"
            
    # Status Effects
    markdown += "## Status Effects\n\n"
    for mech in mechanics_data.status_effects:
        markdown += f"### {mech.name}\n"
        markdown += f"{mech.description}\n\n"
        if mech.sub_mechanics:
            for sub in mech.sub_mechanics:
                markdown += f"- **{sub['name']}**: {sub['description']}\n"
            markdown += "\n"
            
    # Gameplay Mechanics
    markdown += "## Gameplay Mechanics\n\n"
    for mech in mechanics_data.gameplay_mechanics:
        markdown += f"### {mech.name}\n"
        markdown += f"{mech.description}\n\n"
        if mech.sub_mechanics:
            for sub in mech.sub_mechanics:
                markdown += f"- **{sub['name']}**: {sub['description']}\n"
            markdown += "\n"
            
    return markdown

async def extract_mechanics(api_key: str):
    url = "https://dota2.fandom.com/wiki/Mechanics"
    
    extraction_instruction = """
    Analisis halaman wiki Dota 2 Mechanics dan ekstrak informasi berikut dalam format object/dictionary (bukan list):
    - Unit Mechanics (termasuk hero mechanics, stats, dll)
    - Attack Mechanics (damage types, modifiers, dll) 
    - World Mechanics (map, buildings, items, dll)
    - Status Effects (disables, buffs/debuffs, dll)
    - Gameplay Mechanics (roles, farming, dll)
    
    Untuk setiap mechanic, ambil:
    - Nama mechanic
    - Deskripsi lengkap
    - Sub-mechanics jika ada
    
    Format output harus berupa single object dengan properti:
    {
        "unit_mechanics": [...],
        "attack_mechanics": [...],
        "world_mechanics": [...],
        "status_effects": [...],
        "gameplay_mechanics": [...]
    }
    """

    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=url,
                extraction_strategy=LLMExtractionStrategy(
                    provider="openai/gpt-4o-mini",
                    api_token=api_key,
                    schema=DotaMechanics.model_json_schema(),
                    extraction_type="model_json_schema", 
                    instruction=extraction_instruction,
                    temperature=0.3,
                    verbose=True
                ),
                cache_mode=CacheMode.DISABLED
            )

            if not result.extracted_content:
                print("Tidak ada konten yang diekstrak")
                return None

            mechanics_data = json.loads(result.extracted_content)
            
            # Pastikan data dalam format yang benar
            if isinstance(mechanics_data, list):
                mechanics_data = mechanics_data[0]
                
            # Convert ke markdown
            markdown_content = convert_to_markdown(DotaMechanics(**mechanics_data))
            
            # Buat folder docs jika belum ada
            os.makedirs("docs", exist_ok=True)
            
            # Simpan ke file markdown
            with open("docs/mechanics.md", "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            print("Data mechanics berhasil disimpan ke docs/mechanics.md")
            return markdown_content

    except Exception as e:
        print(f"Error saat ekstraksi: {str(e)}")
        return None

if __name__ == "__main__":
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    asyncio.run(extract_mechanics(api_key)) 