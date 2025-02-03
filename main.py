from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai import AsyncWebCrawler, CacheMode
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from urllib.parse import urlparse
from abc import ABC, abstractmethod

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
    
class DotaHeroExtractor(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def extract(self, url: str):
        pass

    @abstractmethod
    def get_base_url(self) -> str:
        pass
        
    @abstractmethod
    async def _extract_hero_info(self, url: str, extraction_instruction: str):
        pass

class DotabuffExtractor(DotaHeroExtractor):
    def get_base_url(self) -> str:
        return "https://www.dotabuff.com"

    async def extract(self, url: str):
        extraction_instruction = """
        Analisis konten website Dotabuff dan ekstrak data berikut:
        // ... existing Dotabuff instruction ...
        """
        return await self._extract_hero_info(url, extraction_instruction)

    async def _extract_hero_info(self, url: str, extraction_instruction: str):
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                raw_result = await crawler.arun(
                    url=url,
                    word_count_threshold=1,
                    extraction_strategy=LLMExtractionStrategy(
                        provider="openai/gpt-4o-mini",
                        api_token=self.api_key,
                        schema=DotaHeroInfo.model_json_schema(),
                        extraction_type="model_json_schema",
                        instruction=extraction_instruction,
                        temperature=0.3,
                        verbose=True
                    ),
                    cache_mode=CacheMode.DISABLED
                )

                if not raw_result.extracted_content:
                    print("Tidak ada konten yang diekstrak")
                    return None

                # Parse JSON
                try:
                    hero_data = json.loads(raw_result.extracted_content)
                    if isinstance(hero_data, list):
                        hero_data = hero_data[0]
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {str(e)}")
                    return None

                # Format ke markdown
                template = """# {name} ({patch})

## Overview
{overview}

## Hero Attributes
| ![Strength]({str_icon}) | ![Agility]({agi_icon}) | ![Intelligence]({int_icon}) |
|------------------------|------------------------|----------------------------|
| {strength}             | {agility}              | {intelligence}            |

## Base Stats
| Attribute | Value |
|-----------|-------|
| Movement Speed | `{movement_speed}` |
| Turn Rate | `{turn_rate}` |
| Vision Range | `{vision_range}` |
| Attack Range | `{attack_range}` |
| Attack Speed | `{attack_speed}` |
| Attack Point | `{attack_point}` |
| Base Armor | `{armor}` |
| Base Attack Time | `{base_attack_time}` |
| Damage | `{damage}` |

## Roles
{roles}

## Abilities
{abilities}

## Talent Tree
------------
Kiri | Level | Kanan
------|--------|-------
{talent_tree}

## Lore
> {lore}

## Additional Information
- Voice Actor: {voice_actor}
- Release Date: {release_date}

_Last Updated: {last_updated}_

Source: [{source}]({source_url})
"""

                # Format data
                markdown_content = template.format(
                    name=hero_data.get('name', 'Unknown'),
                    patch=hero_data.get('patch', 'Unknown'),
                    overview=hero_data.get('overview', 'No overview available'),
                    str_icon=hero_data.get('stats', {}).get('str_icon', ''),
                    agi_icon=hero_data.get('stats', {}).get('agi_icon', ''),
                    int_icon=hero_data.get('stats', {}).get('int_icon', ''),
                    strength=hero_data.get('stats', {}).get('strength', 'N/A'),
                    agility=hero_data.get('stats', {}).get('agility', 'N/A'),
                    intelligence=hero_data.get('stats', {}).get('intelligence', 'N/A'),
                    movement_speed=hero_data.get('stats', {}).get('movement_speed', 'N/A'),
                    turn_rate=hero_data.get('stats', {}).get('turn_rate', 'N/A'),
                    vision_range=hero_data.get('stats', {}).get('vision_range', 'N/A'),
                    attack_range=hero_data.get('stats', {}).get('attack_range', 'N/A'),
                    attack_speed=hero_data.get('stats', {}).get('attack_speed', 'N/A'),
                    attack_point=hero_data.get('stats', {}).get('attack_point', 'N/A'),
                    armor=hero_data.get('stats', {}).get('armor', 'N/A'),
                    base_attack_time=hero_data.get('stats', {}).get('base_attack_time', 'N/A'),
                    damage=hero_data.get('stats', {}).get('damage', 'N/A'),
                    roles='\n'.join([f"- {role}" for role in hero_data.get('roles', [])]),
                    abilities=self._format_abilities(hero_data.get('abilities', [])),
                    talent_tree=self._format_talents(hero_data.get('talents', [])),
                    lore=hero_data.get('lore', 'No lore available'),
                    voice_actor=hero_data.get('voice_actor', 'Unknown'),
                    release_date=hero_data.get('release_date', 'Unknown'),
                    last_updated=hero_data.get('last_updated', '2025-02-03T00:00:00Z'),
                    source='dotabuff.com',
                    source_url=url
                )

                # Save to file
                hero_name = hero_data.get('name', '').lower().replace(' ', '_')
                if not hero_name:
                    hero_name = url.split('/')[-2].lower()

                output_file = f"{hero_name}.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                print(f"\nBerhasil mengekstrak dan memformat data hero")
                print(f"Data tersimpan di: {output_file}")

                return markdown_content

        except Exception as e:
            print(f"Error saat ekstraksi: {str(e)}")
            return None

    def _format_abilities(self, abilities):
        """Helper method untuk format abilities"""
        return chr(10).join([f"""### {ability.get('name', '')} ({ability.get('key', '')})
![{ability.get('name', '')}]({ability.get('image_url', '')})

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
""" for ability in abilities])

    def _format_talents(self, talents):
        """Helper method untuk format talents"""
        return chr(10).join([
            f"{talent.get('left_talent', 'N/A')} | {talent.get('level', 'N/A')} | {talent.get('right_talent', 'N/A')}"
            for talent in sorted(talents, key=lambda x: int(x.get('level', 0)), reverse=True)
        ])

class LiquipediaExtractor(DotaHeroExtractor):
    def get_base_url(self) -> str:
        return "https://liquipedia.net"

    async def extract(self, url: str):
        extraction_instruction = """
        Analisis konten website Liquipedia Dota 2 dan ekstrak data berikut:

        1. Nama hero dan versi patch terkini
        2. Overview/deskripsi hero
        3. Stats dasar:
           - Strength, Agility, Intelligence (base + gain)
           - Movement speed, Sight range, Armor
           - Base attack time, Damage, Attack point
           - Attack speed, Animation
           - Turn rate, Vision range
           - URL icon untuk str/agi/int

        4. Abilities (sangat penting, ambil semua):
           - Nama ability
           - Hotkey ability
           - Tipe ability (Active/Passive)
           - Tipe damage (jika ada)
           - Target/affects
           - Pierces spell immunity
           - Dispellable status
           - Deskripsi lengkap
           - Effects/stats
           - Cast point/Animation
           - Cooldown
           - Mana cost
           - Notes tambahan
           - URL icon ability

        5. Talents:
           - Level (10/15/20/25)
           - Talent kiri dan kanan
           - Bonus attributes

        6. Informasi tambahan:
           - Roles (Carry, Support, etc)
           - Lore/Bio
           - Release date
           - Last updated
           - Voice actor

    Untuk gambar/icon:
        - Cari element img dengan class 'spellcard-wrapper'
        - Ambil URL dari attribute data-src atau src
        - Untuk ability icons, cari di dalam div class 'ability-background'
        - Untuk attribute icons, cari di dalam table class 'infobox-cell'
        - Format URL gambar harus lengkap, contoh:
          https://liquipedia.net/commons/images/f/fa/Static_Remnant_abilityicon_dota2_gameasset.png
        """

        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                raw_result = await crawler.arun(
                    url=url,
                    word_count_threshold=1,
                    extraction_strategy=LLMExtractionStrategy(
                        provider="openai/gpt-4o-mini",
                        api_token=self.api_key,
                        schema=DotaHeroInfo.model_json_schema(),
                        extraction_type="model_json_schema",
                        instruction=extraction_instruction,
                        temperature=0.3,
                        verbose=True
                    ),
                    cache_mode=CacheMode.DISABLED
                )

                if not raw_result.extracted_content:
                    print("Tidak ada konten yang diekstrak")
                    return None

                # Parse JSON
                try:
                    hero_data = json.loads(raw_result.extracted_content)
                    if isinstance(hero_data, list):
                        hero_data = hero_data[0]
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {str(e)}")
                    return None

                # Format ke markdown
                template = """# {name} ({patch})

## Overview
{overview}

## Hero Attributes
| ![Strength]({str_icon}) | ![Agility]({agi_icon}) | ![Intelligence]({int_icon}) |
|------------------------|------------------------|----------------------------|
| {strength}             | {agility}              | {intelligence}            |

## Base Stats
| Attribute | Value |
|-----------|-------|
| Movement Speed | `{movement_speed}` |
| Turn Rate | `{turn_rate}` |
| Vision Range | `{vision_range}` |
| Attack Range | `{attack_range}` |
| Attack Speed | `{attack_speed}` |
| Attack Point | `{attack_point}` |
| Base Armor | `{armor}` |
| Base Attack Time | `{base_attack_time}` |
| Damage | `{damage}` |

## Roles
{roles}

## Abilities
{abilities}

## Talent Tree
------------
Kiri | Level | Kanan
------|--------|-------
{talent_tree}

## Lore
> {lore}

## Additional Information
- Voice Actor: {voice_actor}
- Release Date: {release_date}

_Last Updated: {last_updated}_

Source: [{source}]({source_url})
"""

                # Format data
                markdown_content = template.format(
                    name=hero_data.get('name', 'Unknown'),
                    patch=hero_data.get('patch', 'Unknown'),
                    overview=hero_data.get('overview', 'No overview available'),
                    str_icon=hero_data.get('stats', {}).get('str_icon', ''),
                    agi_icon=hero_data.get('stats', {}).get('agi_icon', ''),
                    int_icon=hero_data.get('stats', {}).get('int_icon', ''),
                    strength=hero_data.get('stats', {}).get('strength', 'N/A'),
                    agility=hero_data.get('stats', {}).get('agility', 'N/A'),
                    intelligence=hero_data.get('stats', {}).get('intelligence', 'N/A'),
                    movement_speed=hero_data.get('stats', {}).get('movement_speed', 'N/A'),
                    turn_rate=hero_data.get('stats', {}).get('turn_rate', 'N/A'),
                    vision_range=hero_data.get('stats', {}).get('vision_range', 'N/A'),
                    attack_range=hero_data.get('stats', {}).get('attack_range', 'N/A'),
                    attack_speed=hero_data.get('stats', {}).get('attack_speed', 'N/A'),
                    attack_point=hero_data.get('stats', {}).get('attack_point', 'N/A'),
                    armor=hero_data.get('stats', {}).get('armor', 'N/A'),
                    base_attack_time=hero_data.get('stats', {}).get('base_attack_time', 'N/A'),
                    damage=hero_data.get('stats', {}).get('damage', 'N/A'),
                    roles='\n'.join([f"- {role}" for role in hero_data.get('roles', [])]),
                    abilities=self._format_abilities(hero_data.get('abilities', [])),
                    talent_tree=self._format_talents(hero_data.get('talents', [])),
                    lore=hero_data.get('lore', 'No lore available'),
                    voice_actor=hero_data.get('voice_actor', 'Unknown'),
                    release_date=hero_data.get('release_date', 'Unknown'),
                    last_updated=hero_data.get('last_updated', '2025-02-03T00:00:00Z'),
                    source='liquipedia.net',
                    source_url=url
                )

                # Save to file
                hero_name = hero_data.get('name', '').lower().replace(' ', '_')
                if not hero_name:
                    hero_name = url.split('/')[-1].lower()

                output_file = f"{hero_name}.md"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                print(f"\nBerhasil mengekstrak dan memformat data hero")
                print(f"Data tersimpan di: {output_file}")

                return markdown_content

        except Exception as e:
            print(f"Error saat ekstraksi: {str(e)}")
            return None

    def _format_abilities(self, abilities):
        """Helper method untuk format abilities"""
        return chr(10).join([f"""### {ability.get('name', '')} ({ability.get('key', '')})
![{ability.get('name', '')}]({ability.get('image_url', '')})

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
""" for ability in abilities])

    def _format_talents(self, talents):
        """Helper method untuk format talents"""
        return chr(10).join([
            f"{talent.get('left_talent', 'N/A')} | {talent.get('level', 'N/A')} | {talent.get('right_talent', 'N/A')}"
            for talent in sorted(talents, key=lambda x: int(x.get('level', 0)), reverse=True)
        ])

class DotaOfficialExtractor(DotaHeroExtractor):
    def get_base_url(self) -> str:
        return "https://www.dota2.com"

    async def extract(self, url: str):
        extraction_instruction = """
        Analisis konten website Dota 2 Official dan ekstrak data berikut:
        // ... Dota2.com specific instruction ...
        """
        return await self._extract_hero_info(url, extraction_instruction)

def get_extractor(url: str, api_key: str) -> DotaHeroExtractor:
    domain = urlparse(url).netloc.lower()
    if "dotabuff.com" in domain:
        return DotabuffExtractor(api_key)
    elif "liquipedia.net" in domain:
        return LiquipediaExtractor(api_key)
    elif "dota2.com" in domain:
        return DotaOfficialExtractor(api_key)
    else:
        raise ValueError(f"Unsupported domain: {domain}")

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
    URL gambar biasanya dalam format: https://www.dotabuff.com/assets...
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
                
            print(f"\nSuccessfully extracted and formatted hero data")
            print(f"Data saved to: {output_file}")
            
            return markdown_content
            
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return None

async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY tidak ditemukan")
    
    hero_urls = [
        "https://www.dotabuff.com/heroes/venomancer/abilities"
    ]
    # hero_urls = [
    #     # Strength Heroes
    #     "https://www.dotabuff.com/heroes/alchemist/abilities",
    #     "https://www.dotabuff.com/heroes/axe/abilities", 
    #     "https://www.dotabuff.com/heroes/bristleback/abilities",
    #     "https://www.dotabuff.com/heroes/centaur-warrunner/abilities",
    #     "https://www.dotabuff.com/heroes/chaos-knight/abilities",
    #     "https://www.dotabuff.com/heroes/dawnbreaker/abilities",
    #     "https://www.dotabuff.com/heroes/doom/abilities",
    #     "https://www.dotabuff.com/heroes/dragon-knight/abilities",
    #     "https://www.dotabuff.com/heroes/earth-spirit/abilities",
    #     "https://www.dotabuff.com/heroes/earthshaker/abilities",
    #     "https://www.dotabuff.com/heroes/elder-titan/abilities",
    #     "https://www.dotabuff.com/heroes/huskar/abilities",
    #     "https://www.dotabuff.com/heroes/kunkka/abilities",
    #     "https://www.dotabuff.com/heroes/legion-commander/abilities",
    #     "https://www.dotabuff.com/heroes/lifestealer/abilities",
    #     "https://www.dotabuff.com/heroes/mars/abilities",
    #     "https://www.dotabuff.com/heroes/night-stalker/abilities",
    #     "https://www.dotabuff.com/heroes/ogre-magi/abilities",
    #     "https://www.dotabuff.com/heroes/omniknight/abilities",
    #     "https://www.dotabuff.com/heroes/primal-beast/abilities",
    #     "https://www.dotabuff.com/heroes/pudge/abilities",
    #     "https://www.dotabuff.com/heroes/slardar/abilities",
    #     "https://www.dotabuff.com/heroes/spirit-breaker/abilities",
    #     "https://www.dotabuff.com/heroes/sven/abilities",
    #     "https://www.dotabuff.com/heroes/tidehunter/abilities",
    #     "https://www.dotabuff.com/heroes/timbersaw/abilities",
    #     "https://www.dotabuff.com/heroes/tiny/abilities",
    #     "https://www.dotabuff.com/heroes/treant-protector/abilities",
    #     "https://www.dotabuff.com/heroes/tusk/abilities",
    #     "https://www.dotabuff.com/heroes/underlord/abilities",
    #     "https://www.dotabuff.com/heroes/undying/abilities",
    #     "https://www.dotabuff.com/heroes/wraith-king/abilities",
        
    #     # Agility Heroes
    #     "https://www.dotabuff.com/heroes/anti-mage/abilities",
    #     "https://www.dotabuff.com/heroes/arc-warden/abilities",
    #     "https://www.dotabuff.com/heroes/bloodseeker/abilities", 
    #     "https://www.dotabuff.com/heroes/bounty-hunter/abilities",
    #     "https://www.dotabuff.com/heroes/clinkz/abilities",
    #     "https://www.dotabuff.com/heroes/drow-ranger/abilities",
    #     "https://www.dotabuff.com/heroes/ember-spirit/abilities",
    #     "https://www.dotabuff.com/heroes/faceless-void/abilities",
    #     "https://www.dotabuff.com/heroes/gyrocopter/abilities",
    #     "https://www.dotabuff.com/heroes/hoodwink/abilities",
    #     "https://www.dotabuff.com/heroes/juggernaut/abilities",
    #     "https://www.dotabuff.com/heroes/luna/abilities",
    #     "https://www.dotabuff.com/heroes/medusa/abilities",
    #     "https://www.dotabuff.com/heroes/meepo/abilities",
    #     "https://www.dotabuff.com/heroes/monkey-king/abilities",
    #     "https://www.dotabuff.com/heroes/morphling/abilities",
    #     "https://www.dotabuff.com/heroes/naga-siren/abilities",
    #     "https://www.dotabuff.com/heroes/phantom-assassin/abilities",
    #     "https://www.dotabuff.com/heroes/phantom-lancer/abilities",
    #     "https://www.dotabuff.com/heroes/razor/abilities",
    #     "https://www.dotabuff.com/heroes/riki/abilities",
    #     "https://www.dotabuff.com/heroes/shadow-fiend/abilities",
    #     "https://www.dotabuff.com/heroes/slark/abilities",
    #     "https://www.dotabuff.com/heroes/sniper/abilities",
    #     "https://www.dotabuff.com/heroes/spectre/abilities",
    #     "https://www.dotabuff.com/heroes/templar-assassin/abilities",
    #     "https://www.dotabuff.com/heroes/terrorblade/abilities",
    #     "https://www.dotabuff.com/heroes/troll-warlord/abilities",
    #     "https://www.dotabuff.com/heroes/ursa/abilities",
    #     "https://www.dotabuff.com/heroes/viper/abilities",
    #     "https://www.dotabuff.com/heroes/weaver/abilities",

    #     # Intelligence Heroes
    #     "https://www.dotabuff.com/heroes/ancient-apparition/abilities",
    #     "https://www.dotabuff.com/heroes/crystal-maiden/abilities",
    #     "https://www.dotabuff.com/heroes/death-prophet/abilities",
    #     "https://www.dotabuff.com/heroes/disruptor/abilities",
    #     "https://www.dotabuff.com/heroes/enchantress/abilities",
    #     "https://www.dotabuff.com/heroes/grimstroke/abilities",
    #     "https://www.dotabuff.com/heroes/jakiro/abilities",
    #     "https://www.dotabuff.com/heroes/keeper-of-the-light/abilities",
    #     "https://www.dotabuff.com/heroes/leshrac/abilities",
    #     "https://www.dotabuff.com/heroes/lich/abilities",
    #     "https://www.dotabuff.com/heroes/lina/abilities",
    #     "https://www.dotabuff.com/heroes/lion/abilities",
    #     "https://www.dotabuff.com/heroes/natures-prophet/abilities",
    #     "https://www.dotabuff.com/heroes/necrophos/abilities",
    #     "https://www.dotabuff.com/heroes/oracle/abilities",
    #     "https://www.dotabuff.com/heroes/outworld-destroyer/abilities",
    #     "https://www.dotabuff.com/heroes/puck/abilities",
    #     "https://www.dotabuff.com/heroes/pugna/abilities",
    #     "https://www.dotabuff.com/heroes/queen-of-pain/abilities",
    #     "https://www.dotabuff.com/heroes/rubick/abilities",
    #     "https://www.dotabuff.com/heroes/shadow-demon/abilities",
    #     "https://www.dotabuff.com/heroes/shadow-shaman/abilities",
    #     "https://www.dotabuff.com/heroes/silencer/abilities",
    #     "https://www.dotabuff.com/heroes/skywrath-mage/abilities",
    #     "https://www.dotabuff.com/heroes/storm-spirit/abilities",
    #     "https://www.dotabuff.com/heroes/tinker/abilities",
    #     "https://www.dotabuff.com/heroes/warlock/abilities",
    #     "https://www.dotabuff.com/heroes/witch-doctor/abilities",
    #     "https://www.dotabuff.com/heroes/zeus/abilities"
    # ]
    
    for url in hero_urls:
        try:
            extractor = get_extractor(url, api_key)
            markdown_content = await extractor.extract(url)
            if markdown_content:
                print(f"\nEkstraksi dari {extractor.__class__.__name__} selesai.")
                print("-" * 50)
        except Exception as e:
            print(f"Error saat ekstraksi dari {url}: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())