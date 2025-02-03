from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai import AsyncWebCrawler, CacheMode
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from urllib.parse import urlparse

class HeroStats(BaseModel):
    strength: str = Field(..., description="Base strength + gain")
    agility: str = Field(..., description="Base agility + gain")
    intelligence: str = Field(..., description="Base intelligence + gain")
    str_icon: str = Field(..., description="Strength icon URL")
    agi_icon: str = Field(..., description="Agility icon URL")
    int_icon: str = Field(..., description="Intelligence icon URL")
    movement_speed: str = Field(..., description="Movement speed")
    sight_range: str = Field(..., description="Day/Night sight range")
    armor: str = Field(..., description="Base armor")
    base_attack_time: str = Field(..., description="Base attack time")
    damage: str = Field(..., description="Damage range")
    attack_point: str = Field(..., description="Attack point")

# Model untuk talent
class HeroTalent(BaseModel):
    level: str = Field(..., description="Talent level")
    left_talent: str = Field(..., description="Left talent option")
    right_talent: str = Field(..., description="Right talent option")

# Model untuk skill
class HeroSkill(BaseModel):
    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    mana_cost: Optional[str] = Field(None, description="Skill mana cost")
    cooldown: Optional[str] = Field(None, description="Skill cooldown")
    images: str = Field(None, description="Skill images")

# Model untuk ability
class HeroAbility(BaseModel):
    name: str = Field(..., description="Ability name")
    key: str = Field(..., description="Ability hotkey")
    ability_type: str = Field(..., description="Ability type")
    damage_type: str = Field(None, description="Damage type")
    affects: str = Field(None, description="What it affects")
    pierces_immunity: str = Field(None, description="Pierces spell immunity")
    dispellable: str = Field(None, description="Dispellable status")
    description: str = Field(..., description="Ability description")
    effects: List[str] = Field(..., description="Ability effects/stats")
    cast_point: str = Field(None, description="Cast point")
    cooldown: str = Field(None, description="Cooldown")
    mana_cost: str = Field(None, description="Mana cost")
    notes: str = Field(None, description="Additional notes")
    image_url: str = Field(..., description="Ability icon URL")

# Model utama hero
class DotaHeroInfo(BaseModel):
    patch: str = Field(..., description="Patch hero")
    name: str = Field(..., description="Hero name")
    overview: str = Field(..., description="Hero overview")
    attributes: dict = Field(..., description="Hero attributes (attack type, primary attr, complexity)")
    stats: HeroStats = Field(..., description="Hero stats")
    facets: List[str] = Field(..., description="Hero facets")
    talents: List[HeroTalent] = Field(..., description="Hero talents")
    skills: List[HeroSkill] = Field(..., description="Hero skills")
    lore: str = Field(..., description="Hero lore/bio")
    roles: List[str] = Field(..., description="Hero roles")
    abilities: List[HeroAbility] = Field(..., description="Hero abilities")
    model_info: str = Field(..., description="Hero model information")
    images: str = Field(None, description="Hero images")
    
async def extract_hero_info(hero_url: str, api_key: str):
    """
    Extract Dota 2 hero information using LLM-based extraction
    
    Args:
        hero_url (str): URL of the hero page
        api_key (str): OpenAI API key
    """
    print(f"\n--- Extracting Hero Information from {hero_url} ---")
    
    extraction_instruction = """
    Analisis konten website informasi hero Dota2 dari Dotabuff dan ekstrak data berikut:

    1. Nama hero
    2. Overview/deskripsi hero
    3. Stats dasar:
       - Strength, Agility, Intelligence (base + gain)
       - Movement speed, Sight range, Armor
       - Base attack time, Damage, Attack point
       - URL icon untuk str/agi/int

    4. Abilities (sangat penting, ambil semua):
       - Nama ability
       - Hotkey ability
       - Tipe ability
       - Tipe damage (jika ada)
       - Target/affects
       - Pierces spell immunity
       - Dispellable status
       - Deskripsi lengkap
       - Effects/stats
       - Cast point
       - Cooldown
       - Mana cost
       - Notes tambahan
       - URL icon ability

    5. Talents:
       - Level (10/15/20/25)
       - Talent kiri
       - Talent kanan

    Pastikan untuk mengambil semua abilities hero dengan lengkap termasuk URL gambar/icon dari Dotabuff.
    URL gambar biasanya dalam format: https://www.dotabuff.com/assets/...
    """

    markdown_instruction = """
    Ubah hasil ekstraksi berikut menjadi format markdown yang rapi dengan aturan:
    1. Gunakan heading yang tepat (# untuk judul utama, ## untuk sub judul)
    2. Gunakan tabel untuk data yang berbentuk tabel
    3. Gunakan bullet points (-) untuk daftar
    4. Tambahkan line breaks yang sesuai
    5. Format code atau nilai penting dengan `backtick`
    6. Gunakan > untuk quotes atau lore
    7. Tambahkan horizontal rule (---) untuk memisahkan section penting
    """

    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            # Ekstraksi pertama - tetap gunakan JSON untuk data terstruktur
            raw_result = await crawler.arun(
                url=hero_url,
                word_count_threshold=1,
                extraction_strategy=LLMExtractionStrategy(
                    provider="openai/gpt-4o-mini",
                    api_token=api_key,
                    schema=DotaHeroInfo.model_json_schema(),
                    extraction_type="model_json_schema",  # Gunakan JSON dulu
                    instruction=extraction_instruction,
                    temperature=0.3,
                    verbose=True
                ),
                cache_mode=CacheMode.DISABLED
            )
            
            if not raw_result.extracted_content:
                print("Tidak ada konten yang diekstrak")
                return None

            # Parse JSON dulu
            try:
                hero_data = json.loads(raw_result.extracted_content)
                if isinstance(hero_data, list):
                    hero_data = hero_data[0]
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                return None

            # Helper function untuk format skills
            def format_skill(skill):
                return f"""### {skill['name']}
![Skill Icon]({skill.get('images', '')})
- Description: {skill['description']}
- Mana Cost: `{skill.get('mana_cost', 'N/A')}`
- Cooldown: `{skill.get('cooldown', 'N/A')}`"""

            # Helper function untuk format abilities
            def format_ability(ability):
                effects = '\n'.join(f"  - {effect}" for effect in ability['effects'])
                return f"""### {ability['name']}
![Ability Icon]({ability.get('images', '')})
- Description: {ability['description']}
- Effects:
{effects}
- Mana Cost: `{ability.get('mana_cost', 'N/A')}`
- Cooldown: `{ability.get('cooldown', 'N/A')}`"""

            # Template untuk skills
            def format_skills(skills_data):
                if not skills_data:
                    return ''
                
                skills_list = []
                for skill in skills_data:
                    skill_text = f"""### {skill['name']}
![{skill['name']}](https://liquipedia.net{skill.get('images', '')})
- Description: {skill['description']}
- Mana Cost: `{skill.get('mana_cost', 'N/A')}`
- Cooldown: `{skill.get('cooldown', 'N/A')}`"""
                    skills_list.append(skill_text)
                
                return "## Skills\n" + "\n\n".join(skills_list) if skills_list else ''

            # Template untuk markdown
            template = """# {name}

## Overview
{overview}

## Hero Attributes
| ![Strength]({str_icon}) | ![Agility]({agi_icon}) | ![Intelligence]({int_icon}) |
|------------------------|------------------------|----------------------------|
| {strength}             | {agility}              | {intelligence}            |

| Attribute | Value |
|-----------|-------|
| Movement speed | {movement_speed} |
| Sight range | {sight_range} |
| Armor | {armor} |
| Base attack time | {base_attack_time} |
| Damage | {damage} |
| Attack point | {attack_point} |

## Talent Tree
------------
Kiri | Level | Kanan
------|--------|-------
{talent_tree}

## Abilities
{abilities}

_Last Updated: {last_updated}_

Source: [{source}]({source_url})
"""

            # Helper function untuk format URL gambar
            def format_image_url(url):
                if not url:
                    return ''
                if url.startswith('http'):
                    return url
                if url.startswith('/assets'):
                    return f"https://www.dotabuff.com{url}"
                return f"https://www.dotabuff.com/assets/{url}"

            # Get domain from URL
            domain = urlparse(hero_url).netloc.replace('www.', '')

            # Format data dengan pengecekan yang lebih aman
            markdown_content = template.format(
                name=hero_data.get('name', 'Unknown'),
                overview=hero_data.get('overview', 'No overview available'),
                str_icon=format_image_url(hero_data.get('stats', {}).get('str_icon', '')),
                agi_icon=format_image_url(hero_data.get('stats', {}).get('agi_icon', '')),
                int_icon=format_image_url(hero_data.get('stats', {}).get('int_icon', '')),
                strength=hero_data.get('stats', {}).get('strength', 'N/A'),
                agility=hero_data.get('stats', {}).get('agility', 'N/A'),
                intelligence=hero_data.get('stats', {}).get('intelligence', 'N/A'),
                movement_speed=hero_data.get('stats', {}).get('movement_speed', 'N/A'),
                sight_range=hero_data.get('stats', {}).get('sight_range', 'N/A'),
                armor=hero_data.get('stats', {}).get('armor', 'N/A'),
                base_attack_time=hero_data.get('stats', {}).get('base_attack_time', 'N/A'),
                damage=hero_data.get('stats', {}).get('damage', 'N/A'),
                attack_point=hero_data.get('stats', {}).get('attack_point', 'N/A'),
                abilities=chr(10).join([f"""### {ability.get('name', '')} ({ability.get('key', '')})
![{ability.get('name', '')}]({format_image_url(ability.get('image_url', ''))})

**Type**: {ability.get('ability_type', 'N/A')}
{f"**Damage Type**: {ability.get('damage_type')}" if ability.get('damage_type') else ''}
{f"**Affects**: {ability.get('affects')}" if ability.get('affects') else ''}
{f"**Pierces Spell Immunity**: {ability.get('pierces_immunity')}" if ability.get('pierces_immunity') else ''}
{f"**Dispellable**: {ability.get('dispellable')}" if ability.get('dispellable') else ''}

{ability.get('description', 'No description available')}

**Effects**:
{chr(10).join([f"- {effect}" for effect in ability.get('effects', [])])}

{f"**Cast Point**: {ability.get('cast_point')}" if ability.get('cast_point') else ''}
{f"**Cooldown**: {ability.get('cooldown')}" if ability.get('cooldown') else ''}
{f"**Mana Cost**: {ability.get('mana_cost')}" if ability.get('mana_cost') else ''}

{f"*{ability.get('notes')}*" if ability.get('notes') else ''}
""" for ability in hero_data.get('abilities', [])]),
                talent_tree=chr(10).join([
                    f"{talent.get('left_talent', 'N/A')} | {talent.get('level', 'N/A')} | {talent.get('right_talent', 'N/A')}"
                    for talent in sorted(
                        hero_data.get('talents', []),
                        key=lambda x: int(x.get('level', 0)),
                        reverse=True
                    )
                ]),
                last_updated=hero_data.get('last_updated', '2025-02-03T00:00:00Z'),
                source=domain,
                source_url=hero_url
            )
            
            # Simpan hasil markdown dengan nama hero
            hero_name = hero_data.get('name', '').lower().replace(' ', '_')
            if not hero_name:
                hero_name = hero_url.split('/')[-2].lower()  # Ambil dari URL jika nama tidak ada
            
            output_file = f"{hero_name}.md"
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            print(f"\nBerhasil mengekstrak dan memformat data hero")
            print(f"Data tersimpan di: {output_file}")
            
            return markdown_content
            
    except Exception as e:
        print(f"Error saat ekstraksi: {str(e)}")
        return None

async def main():
    # Ambil API key dari environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY tidak ditemukan dalam environment variables")
    
    # Contoh URL hero Dota 2
    hero_urls = [
        "https://www.dotabuff.com/heroes/alchemist/abilities"
    ]
    
    for url in hero_urls:
        markdown_content = await extract_hero_info(url, api_key)
        if markdown_content:
            print("\nEkstraksi selesai. Silakan cek file markdown untuk detailnya.")
            print("-" * 50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())