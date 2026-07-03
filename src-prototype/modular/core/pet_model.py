"""Pet registry and action metadata helpers for the Tk prototype.

This module is intentionally free of Tk imports. It mirrors the monolith's
pet-family JSON behavior while keeping product defaults free of local private
paths.
"""

from __future__ import annotations

import copy
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

FAMILY_FILE = "pet-family.json"
CELL_W = 192
CELL_H = 208
CUSTOM_ACTION_PREFIX = "custom:"
CUSTOM_ACTION_MAX_FRAMES = 8
BASIC_ATLAS_SIZE = (CELL_W * 8, CELL_H * 9)
FULL_ATLAS_MIN_HEIGHT = CELL_H * 19

ROWS: dict[str, tuple[int, int, list[int]]] = {
    "idle": (0, 6, [260, 150, 150, 170, 170, 320]),
    "running-right": (1, 8, [58, 54, 50, 54, 58, 50, 54, 68]),
    "running-left": (2, 8, [58, 54, 50, 54, 58, 50, 54, 68]),
    "waving": (3, 4, [170, 120, 120, 220]),
    "jumping": (4, 5, [80, 75, 90, 95, 140]),
    "failed": (5, 8, [120, 100, 120, 140, 160, 180, 180, 260]),
    "waiting": (6, 6, [220, 180, 180, 220, 180, 260]),
    "running": (7, 6, [62, 58, 54, 58, 62, 74]),
    "review": (8, 6, [210, 190, 220, 190, 190, 260]),
    "standing": (9, 8, [240, 220, 260, 220, 280, 220, 240, 320]),
    "tongue": (10, 8, [140, 140, 150, 150, 150, 150, 160, 220]),
    "lying": (11, 8, [190, 190, 230, 260, 260, 300, 300, 360]),
    "stretching": (12, 8, [130, 140, 150, 170, 190, 180, 170, 230]),
    "sleeping": (13, 8, [420, 480, 460, 520, 480, 540, 500, 560]),
    "sniffing": (14, 8, [130, 130, 140, 150, 170, 170, 160, 220]),
    "rolling": (15, 8, [120, 110, 110, 115, 115, 110, 120, 180]),
    "crying": (16, 8, [220, 200, 210, 230, 250, 230, 210, 300]),
    "chase-butterfly": (17, 8, [72, 66, 62, 66, 72, 66, 62, 88]),
    "angry": (18, 8, [130, 110, 130, 110, 170, 140, 140, 240]),
}

BASE_ACTIONS = ["waving", "jumping", "waiting", "review", "failed", "running"]
BASE_INTERNAL_ACTIONS = ["idle", "running-right", "running-left", "waving", "jumping"]
BASIC_ATLAS_ACTIONS = ["idle", "running-right", "running-left", "waving", "jumping"]
EXTENDED_ACTIONS = [
    "standing",
    "tongue",
    "lying",
    "stretching",
    "sleeping",
    "sniffing",
    "rolling",
    "crying",
    "chase-butterfly",
    "angry",
]
FULL_SUPPORTED_ACTIONS = ["idle", "running-right", "running-left", *BASE_ACTIONS, *EXTENDED_ACTIONS]
QUICK_MENU_BASE_ACTIONS = ["waving", "running", "jumping", "waiting"]

ACTION_LABELS = {
    "idle": "待机",
    "running-right": "向右跑",
    "running-left": "向左跑",
    "waving": "挥爪",
    "jumping": "跳一下",
    "waiting": "等一下",
    "review": "陪我一会",
    "failed": "委屈一下",
    "running": "跑一小段",
    "stepping": "原地踏步",
    "standing": "站一会",
    "tongue": "吐舌头",
    "lying": "卧倒",
    "stretching": "伸懒腰",
    "sleeping": "打个盹",
    "sniffing": "闻一闻",
    "rolling": "打个滚",
    "crying": "哭一下",
    "chase-butterfly": "追蝴蝶",
    "angry": "生气一下",
}

PET_CATEGORY_GROUP_LABELS = {
    "real_animal": "真实动物",
    "human_character": "人物角色",
    "fantasy_character": "幻想生物",
    "mechanical_object": "机械物件",
    "plant_nature": "植物自然",
    "other": "其他",
}

PET_CATEGORY_TYPE_GROUPS = {
    "canine": "real_animal",
    "feline": "real_animal",
    "rabbit": "real_animal",
    "small_mammal": "real_animal",
    "large_mammal": "real_animal",
    "bird": "real_animal",
    "reptile_amphibian": "real_animal",
    "aquatic": "real_animal",
    "arthropod": "real_animal",
    "human": "human_character",
    "fantasy": "fantasy_character",
    "robot": "mechanical_object",
    "object": "mechanical_object",
    "plant": "plant_nature",
    "custom": "other",
}

PET_CATEGORY_TYPE_LABELS = {
    "canine": "犬科",
    "feline": "猫科",
    "rabbit": "兔类",
    "small_mammal": "小型哺乳",
    "large_mammal": "大型哺乳",
    "bird": "鸟类",
    "reptile_amphibian": "爬行/两栖",
    "aquatic": "水生",
    "arthropod": "节肢",
    "human": "人物",
    "fantasy": "幻想",
    "robot": "机器人",
    "object": "拟物/物件",
    "plant": "植物",
    "custom": "自定义",
}

PET_CATEGORY_SUBTYPE_LABELS = {
    "canine": {
        "small_dog": "小型犬",
        "medium_dog": "中型犬",
        "large_dog": "大型犬",
        "short_leg_dog": "短腿犬",
        "long_hair_dog": "长毛犬",
        "short_hair_dog": "短毛犬",
        "spitz_dog": "尖耳犬",
        "drop_ear_dog": "垂耳犬",
        "wolf_fox": "狼/狐类",
    },
    "feline": {
        "house_cat": "家猫",
        "orange_cat": "橘猫",
        "long_hair_cat": "长毛猫",
        "short_hair_cat": "短毛猫",
        "kitten": "幼猫",
        "big_cat": "大型猫科",
    },
    "rabbit": {"upright_rabbit": "立耳兔", "lop_rabbit": "垂耳兔", "dwarf_rabbit": "侏儒兔"},
    "small_mammal": {
        "hamster": "仓鼠",
        "guinea_pig": "豚鼠",
        "chinchilla": "龙猫",
        "hedgehog": "刺猬",
        "ferret": "雪貂",
        "squirrel": "松鼠",
    },
    "large_mammal": {
        "horse": "马",
        "deer": "鹿",
        "sheep_cow": "羊/牛",
        "panda_bear": "熊猫/熊",
        "elephant": "象",
    },
    "bird": {
        "small_flying_bird": "小型飞鸟",
        "parrot": "鹦鹉",
        "pigeon": "鸽类",
        "poultry": "家禽",
        "waterfowl": "水禽",
        "penguin": "企鹅",
        "raptor": "猛禽",
    },
    "reptile_amphibian": {"turtle": "龟", "lizard": "蜥蜴", "snake": "蛇", "gecko": "守宫", "frog": "蛙"},
    "aquatic": {
        "goldfish": "金鱼",
        "tropical_fish": "热带鱼",
        "jellyfish": "水母",
        "octopus": "章鱼",
        "seahorse": "海马",
        "whale_dolphin": "鲸/海豚",
    },
    "arthropod": {
        "butterfly": "蝴蝶",
        "bee": "蜜蜂",
        "beetle": "甲虫",
        "spider": "蜘蛛",
        "crab_shrimp": "蟹/虾",
    },
    "human": {
        "memorial_person": "纪念人物",
        "q_character": "Q版人物",
        "pixel_person": "像素人物",
        "anime_character": "动漫角色",
        "profession_person": "职业人物",
        "child_person": "儿童",
        "elder_person": "老人",
    },
    "fantasy": {
        "dragon": "龙",
        "elf": "精灵",
        "slime": "史莱姆",
        "unicorn": "独角兽",
        "little_monster": "小怪物",
        "ghost": "幽灵",
        "magic_pet": "魔法宠物",
    },
    "robot": {
        "box_robot": "盒子机器人",
        "humanoid_robot": "人形机器人",
        "mecha": "机甲",
        "device": "设备",
        "vehicle": "载具",
    },
    "object": {
        "plush": "毛绒玩具",
        "cup": "杯子",
        "food": "食物",
        "book": "书本",
        "tool": "工具",
        "furniture": "家具",
    },
    "plant": {
        "potted_plant": "盆栽",
        "flower": "花",
        "sapling": "树苗",
        "succulent": "多肉",
        "mushroom": "蘑菇",
    },
    "custom": {"other": "未知/自定义"},
}

PET_CATEGORY_LOOKUP = {
    subtype_id: {
        "category_group": PET_CATEGORY_TYPE_GROUPS.get(category, "other"),
        "category": category,
        "category_subtype": subtype_id,
        "category_detail": label,
    }
    for category, subtypes in PET_CATEGORY_SUBTYPE_LABELS.items()
    for subtype_id, label in subtypes.items()
}

PET_CATEGORY_ALIASES = {
    "dog": "small_dog",
    "cat": "house_cat",
    "rabbit": "upright_rabbit",
    "small_mammal": "hamster",
    "large_mammal": "horse",
    "bird": "small_flying_bird",
    "reptile": "turtle",
    "reptile_amphibian": "turtle",
    "aquatic": "goldfish",
    "insect": "butterfly",
    "arthropod": "butterfly",
    "human": "q_character",
    "fantasy": "little_monster",
    "robot": "box_robot",
    "object": "plush",
    "plant": "potted_plant",
    "custom": "other",
}


def clamp(value: Any, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = minimum
    return max(minimum, min(maximum, number))


def is_custom_action_id(value: Any) -> bool:
    text = str(value or "")
    return text.startswith(CUSTOM_ACTION_PREFIX) and len(text) > len(CUSTOM_ACTION_PREFIX)


def normalize_pet_category_id(value: Any) -> str:
    category_id = str(value or "").strip()
    if category_id in PET_CATEGORY_LOOKUP:
        return category_id
    return PET_CATEGORY_ALIASES.get(category_id, "")


def infer_pet_category(pet: Mapping[str, Any]) -> str:
    for key in ("category_subtype", "category"):
        category_id = normalize_pet_category_id(pet.get(key))
        if category_id:
            return category_id
    text = " ".join(
        str(pet.get(key) or "")
        for key in ("display_name", "species", "category_detail", "notes")
    ).lower()
    rules = [
        ("long_hair_dog", ("松狮", "厚毛", "长毛犬", "chow")),
        ("short_leg_dog", ("短腿", "柯基", "corgi")),
        ("drop_ear_dog", ("垂耳", "下垂耳")),
        ("short_hair_dog", ("短毛狗", "黑白短毛", "白棕狗")),
        ("orange_cat", ("橘猫", "橘宝", "橘色")),
        ("house_cat", ("猫", "cat")),
        ("small_dog", ("狗", "犬", "dog", "小狗")),
        ("penguin", ("企鹅",)),
        ("parrot", ("鹦鹉",)),
        ("small_flying_bird", ("鸟", "bird")),
        ("turtle", ("龟",)),
        ("goldfish", ("鱼", "fish")),
        ("box_robot", ("盒子机器人", "ai 盒子", "ai盒子")),
        ("humanoid_robot", ("人形机器人",)),
        ("mecha", ("机甲",)),
        ("device", ("设备", "屏幕", "终端")),
        ("vehicle", ("小车", "飞船", "无人机", "载具")),
        ("box_robot", ("机器人", "机械", "robot", "ai")),
        ("memorial_person", ("纪念人物", "真人", "家人")),
        ("q_character", ("人物", "角色", "human", "q版", "人")),
        ("potted_plant", ("盆栽", "植物", "绿植")),
        ("plush", ("玩偶", "毛绒", "物件", "object")),
    ]
    for category_id, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return category_id
    return "other"


def pet_category_fields(category_id: Any, detail: Any = "") -> dict[str, str]:
    normalized_id = normalize_pet_category_id(category_id) or "other"
    fields = dict(PET_CATEGORY_LOOKUP.get(normalized_id, PET_CATEGORY_LOOKUP["other"]))
    custom_detail = str(detail or "").strip()
    if custom_detail:
        fields["category_detail"] = custom_detail
    return fields


def normalize_pet_category_metadata(pet: dict[str, Any]) -> dict[str, Any]:
    category_id = infer_pet_category(pet)
    pet.update(pet_category_fields(category_id, pet.get("category_detail")))
    return pet


def sanitize_pet_slug(name: Any) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(name).strip().lower()).strip("-")
    return slug or f"pet-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def pet_asset_path(pet_dir: str | Path, relative_or_absolute: Any) -> Path | None:
    raw = str(relative_or_absolute or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if path.is_absolute():
        return path
    return Path(pet_dir) / path


def _image_height(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    try:
        from PIL import Image

        with Image.open(path) as image:
            return int(image.height)
    except Exception:
        return 0


def default_pet_family() -> dict[str, Any]:
    """Return product-safe defaults for a clean prototype data directory."""

    return {
        "version": 1,
        "current_pet_id": "danhuang",
        "pets": [
            {
                "id": "danhuang",
                "display_name": "蛋黄",
                "species": "dog",
                "category_group": "real_animal",
                "category": "canine",
                "category_subtype": "short_leg_dog",
                "category_detail": "暖黄短腿小狗，深棕下垂耳",
                "status": "ready",
                "spritesheet": "spritesheet.webp",
                "identity_image": "",
                "reference_images": ["references/01-identity-canonical-base.png"],
                "notes": "暖黄短腿小狗，深棕下垂耳，深色宽圆口鼻，圆黑鼻，温柔略委屈的眼神。",
                "relationship": "主人家里养了 9 年的狗子，是家人。",
                "role_profile": "蛋黄是这个桌宠的核心纪念形象，以温和安静的方式继续陪伴主人。",
                "background": "蛋黄在 2023 年因病离开。桌宠不是要替代真实的蛋黄，而是保存主人和蛋黄之间的陪伴感。",
                "personality": "亲近、安静、真诚，像熟悉主人的小狗，会用陪伴和短句回应。",
                "speech_style": "称呼用户为“主人”。少说教、少工具感，多说“我在”“陪你”“趴着”“摇尾巴”“摸摸头”。想念相关表达要克制。",
                "action_pack_level": "full",
                "supported_actions": list(FULL_SUPPORTED_ACTIONS),
                "extension_assets": [],
            },
            {
                "id": "black_white_dog",
                "display_name": "小墨",
                "species": "dog",
                "category_group": "real_animal",
                "category": "canine",
                "category_subtype": "short_hair_dog",
                "category_detail": "黑白短毛狗",
                "status": "ready",
                "spritesheet": "family/xiao-mo/spritesheet.webp",
                "identity_image": "family/xiao-mo/identity-base.png",
                "reference_images": ["family-references/black-white-dog.jpg", "family/xiao-mo/identity-base.png"],
                "notes": "小墨，黑白短毛狗，黑色下垂耳，黑色双眼罩，白色鼻梁，白色胸口和前腿，安静亲近。",
                "relationship": "主人家里的宠物形象之一，作为独立桌宠陪伴主人。",
                "role_profile": "小墨是安静亲近的黑白小狗，适合用稳定、轻声、靠近的方式陪主人。",
                "background": "当前是基础动作版，先保留稳定的日常陪伴感，后续再补充更多动作。",
                "personality": "安静、贴近、不抢话，适合在主人忙或累的时候默默陪着。",
                "speech_style": "称呼用户为“主人”。短句、轻声、少打扰，不使用客服或工具口吻。",
                "action_pack_level": "basic",
                "supported_actions": list(BASE_INTERNAL_ACTIONS),
                "extension_assets": [],
            },
            {
                "id": "orange_cat",
                "display_name": "橘宝",
                "species": "cat",
                "category_group": "real_animal",
                "category": "feline",
                "category_subtype": "orange_cat",
                "category_detail": "橘色虎斑猫",
                "status": "reference_only",
                "spritesheet": "family/ju-bao/spritesheet.webp",
                "identity_image": "",
                "reference_images": ["family-references/orange-cat-and-hugging-dog.jpg", "family/ju-bao/identity-base.png"],
                "notes": "橘宝，橘色虎斑猫，圆脸，白胡须，温顺眯眼。已拆出独立身份基准图，等待生成动作精灵图。",
                "relationship": "主人家里的橘猫形象之一，作为独立桌宠陪伴主人。",
                "role_profile": "橘宝是带一点猫咪自在感的陪伴角色，会用轻松、靠近但不黏人的方式回应主人。",
                "background": "橘宝来自主人保存的家庭宠物参考图，作为独立宠物形象陪伴主人。",
                "personality": "自在、柔软、偶尔撒娇，回应时比小狗更像猫，温和但有一点自己的节奏。",
                "speech_style": "称呼用户为“主人”。可以更轻松一点，但仍保持短句、亲近、不像 AI 助手。",
                "action_pack_level": "reference",
                "supported_actions": [],
                "extension_assets": [],
            },
            {
                "id": "hugging_dog",
                "display_name": "小白",
                "species": "dog",
                "category_group": "real_animal",
                "category": "canine",
                "category_subtype": "small_dog",
                "category_detail": "白棕小狗",
                "status": "reference_only",
                "spritesheet": "family/xiao-bai/spritesheet.webp",
                "identity_image": "",
                "reference_images": ["family-references/orange-cat-and-hugging-dog.jpg", "family/xiao-bai/identity-base.png"],
                "notes": "小白，白棕狗狗，白脸棕耳，吐舌亲近。已拆出独立身份基准图，等待生成动作精灵图。",
                "relationship": "主人家里的白色小狗形象之一，作为独立桌宠陪伴主人。",
                "role_profile": "小白是温和明亮的小狗陪伴角色，重点是干净、稳定、轻快的陪伴感。",
                "background": "小白来自主人保存的家庭宠物参考图，作为独立宠物形象陪伴主人。",
                "personality": "温顺、亲近、轻快，适合在主人需要一点轻松感时回应。",
                "speech_style": "称呼用户为“主人”。短句、轻快、亲近，避免长篇说教。",
                "action_pack_level": "reference",
                "supported_actions": [],
                "extension_assets": [],
            },
        ],
    }


def normalize_extension_assets(assets: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for asset in assets if isinstance(assets, list) else []:
        if not isinstance(asset, Mapping):
            continue
        action_id = str(asset.get("id") or "").strip()
        label = str(asset.get("label") or "").strip()
        strip = str(asset.get("strip") or "").strip()
        if not strip:
            continue
        if action_id in ROWS:
            label = label or ACTION_LABELS.get(action_id, action_id)
        elif is_custom_action_id(action_id):
            label = label or action_id[len(CUSTOM_ACTION_PREFIX) :]
        else:
            continue
        if action_id in seen:
            continue
        seen.add(action_id)
        try:
            count = int(asset.get("frames") or 0)
        except (TypeError, ValueError):
            count = 0
        count = int(clamp(count, 1, CUSTOM_ACTION_MAX_FRAMES))
        source_durations = asset.get("durations") if isinstance(asset.get("durations"), list) else []
        durations: list[int] = []
        for index in range(count):
            try:
                duration = int(source_durations[index])
            except (IndexError, TypeError, ValueError):
                if action_id in ROWS and index < len(ROWS[action_id][2]):
                    duration = int(ROWS[action_id][2][index])
                else:
                    duration = 180
            durations.append(int(clamp(duration, 60, 900)))
        normalized.append(
            {
                "id": action_id,
                "label": label,
                "strip": strip,
                "frames": count,
                "durations": durations,
            }
        )
    return normalized


def normalize_pet_action_metadata(pet: dict[str, Any], pet_dir: str | Path) -> dict[str, Any]:
    sprite = pet_asset_path(pet_dir, pet.get("spritesheet"))
    height = _image_height(sprite)
    level = str(pet.get("action_pack_level") or "").strip().lower()
    if not level:
        if height >= FULL_ATLAS_MIN_HEIGHT or pet.get("id") == "danhuang":
            level = "full"
        elif height >= BASIC_ATLAS_SIZE[1]:
            level = "basic"
        else:
            level = "reference"

    extension_ids = {asset["id"] for asset in pet.get("extension_assets", [])}
    raw_actions = [
        str(action)
        for action in pet.get("supported_actions", [])
        if str(action) in ROWS or str(action) == "idle" or str(action) in extension_ids
    ]
    raw_actions = list(dict.fromkeys([*raw_actions, *extension_ids]))
    if not raw_actions:
        if level == "full":
            raw_actions = list(FULL_SUPPORTED_ACTIONS)
        elif level == "basic":
            raw_actions = list(BASE_INTERNAL_ACTIONS)
    if level != "full":
        raw_actions = [action for action in raw_actions if action in BASE_INTERNAL_ACTIONS or action in extension_ids]

    identity_image = str(pet.get("identity_image") or "").strip()
    if not identity_image:
        refs = pet.get("reference_images") if isinstance(pet.get("reference_images"), list) else []
        for ref in refs:
            text = str(ref).replace("\\", "/").lower()
            path = pet_asset_path(pet_dir, ref)
            if ("identity" in text or "canonical" in text) and path and path.exists():
                identity_image = str(ref)
                break

    pet["action_pack_level"] = level
    pet["supported_actions"] = list(dict.fromkeys(raw_actions))
    pet["identity_image"] = identity_image
    return pet


def normalize_pet_entry(pet: Mapping[str, Any], pet_dir: str | Path) -> dict[str, Any] | None:
    pet_id = str(pet.get("id", "")).strip()
    if not pet_id:
        return None
    normalized = {
        "id": pet_id,
        "display_name": str(pet.get("display_name") or pet_id),
        "species": str(pet.get("species") or ""),
        "category_group": str(pet.get("category_group") or ""),
        "category": str(pet.get("category") or ""),
        "category_subtype": str(pet.get("category_subtype") or ""),
        "category_detail": str(pet.get("category_detail") or ""),
        "status": str(pet.get("status") or "reference_only"),
        "spritesheet": str(pet.get("spritesheet") or ""),
        "identity_image": str(pet.get("identity_image") or ""),
        "reference_images": pet.get("reference_images") if isinstance(pet.get("reference_images"), list) else [],
        "notes": str(pet.get("notes") or ""),
        "relationship": str(pet.get("relationship") or ""),
        "role_profile": str(pet.get("role_profile") or ""),
        "background": str(pet.get("background") or ""),
        "personality": str(pet.get("personality") or ""),
        "speech_style": str(pet.get("speech_style") or ""),
        "action_pack_level": str(pet.get("action_pack_level") or ""),
        "supported_actions": pet.get("supported_actions") if isinstance(pet.get("supported_actions"), list) else [],
        "extension_assets": normalize_extension_assets(pet.get("extension_assets")),
    }
    normalized = normalize_pet_category_metadata(normalized)
    return normalize_pet_action_metadata(normalized, pet_dir)


def family_path(pet_dir_or_file: str | Path) -> Path:
    path = Path(pet_dir_or_file)
    return path if path.name == FAMILY_FILE else path / FAMILY_FILE


def load_pet_family(pet_dir: str | Path, path: str | Path | None = None) -> dict[str, Any]:
    root = Path(pet_dir)
    file_path = Path(path) if path is not None else family_path(root)
    family = default_pet_family()
    if file_path.exists():
        try:
            saved = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(saved, dict) and isinstance(saved.get("pets"), list):
                family.update(saved)
        except (OSError, ValueError, TypeError):
            pass

    seen: set[str] = set()
    pets: list[dict[str, Any]] = []
    for pet in family.get("pets", []):
        if not isinstance(pet, Mapping):
            continue
        normalized = normalize_pet_entry(pet, root)
        if normalized is None:
            continue
        pet_id = normalized["id"]
        if pet_id in seen:
            continue
        seen.add(pet_id)
        pets.append(normalized)

    if not any(pet["id"] == "danhuang" for pet in pets):
        pets.insert(0, normalize_pet_entry(default_pet_family()["pets"][0], root) or default_pet_family()["pets"][0])

    try:
        family["version"] = int(family.get("version") or 1)
    except (TypeError, ValueError):
        family["version"] = 1
    family["pets"] = pets
    if family.get("current_pet_id") not in {pet["id"] for pet in pets}:
        family["current_pet_id"] = "danhuang"
    return family


def save_pet_family(path: str | Path, family: Mapping[str, Any], current_pet_id: str | None = None) -> None:
    data = copy.deepcopy(dict(family))
    if current_pet_id:
        data["current_pet_id"] = str(current_pet_id)
    target = family_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def pet_by_id(family: Mapping[str, Any], pet_id: str) -> dict[str, Any]:
    pets = family.get("pets") if isinstance(family.get("pets"), list) else []
    for pet in pets:
        if isinstance(pet, Mapping) and pet.get("id") == pet_id:
            return dict(pet)
    if pets and isinstance(pets[0], Mapping):
        return dict(pets[0])
    return default_pet_family()["pets"][0]


def ready_pets(family: Mapping[str, Any]) -> list[dict[str, Any]]:
    pets = family.get("pets") if isinstance(family.get("pets"), list) else []
    return [dict(pet) for pet in pets if isinstance(pet, Mapping) and pet.get("status") == "ready"]


def family_summary(family: Mapping[str, Any]) -> dict[str, Any]:
    pets = family.get("pets") if isinstance(family.get("pets"), list) else []
    status_counts: dict[str, int] = {}
    for pet in pets:
        if not isinstance(pet, Mapping):
            continue
        status = str(pet.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "version": int(family.get("version") or 1),
        "current_pet_id": str(family.get("current_pet_id") or "danhuang"),
        "pet_count": len([pet for pet in pets if isinstance(pet, Mapping)]),
        "ready_count": status_counts.get("ready", 0),
        "status_counts": status_counts,
    }
