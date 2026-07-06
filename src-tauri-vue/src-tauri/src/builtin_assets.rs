pub struct BuiltinAsset {
    pub relative_path: &'static str,
    pub bytes: &'static [u8],
}

pub const BUILTIN_PET_FAMILY_JSON: &str =
    include_str!("../builtin-runtime/danhuang/pet-family.json");

pub const BUILTIN_RUNTIME_ASSETS: &[BuiltinAsset] = &[
    BuiltinAsset {
        relative_path: "spritesheet.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/spritesheet.webp"),
    },
    BuiltinAsset {
        relative_path: "family/danhuang/uploads/user-1-01.jpg",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/danhuang/uploads/user-1-01.jpg"),
    },
    BuiltinAsset {
        relative_path: "family/xiao-mo/identity-base.png",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/xiao-mo/identity-base.png"),
    },
    BuiltinAsset {
        relative_path: "family/xiao-mo/spritesheet.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/xiao-mo/spritesheet.webp"),
    },
    BuiltinAsset {
        relative_path: "family/xiao-bai/identity-base.png",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/xiao-bai/identity-base.png"),
    },
    BuiltinAsset {
        relative_path: "family/xiao-bai/spritesheet.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/xiao-bai/spritesheet.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ju-bao/identity-base.png",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ju-bao/identity-base.png"),
    },
    BuiltinAsset {
        relative_path: "family/ju-bao/spritesheet.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ju-bao/spritesheet.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ju-bao/extension-custom-licking-fur.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ju-bao/extension-custom-licking-fur.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ju-bao/extension-custom-licking-paw.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ju-bao/extension-custom-licking-paw.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ju-bao/extension-custom-washing-face.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ju-bao/extension-custom-washing-face.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/identity-base.png",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/identity-base.png"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/spritesheet.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/spritesheet.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/uploads/user-1-01.jpg",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/uploads/user-1-01.jpg"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/uploads/user-2-01.jpg",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/uploads/user-2-01.jpg"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-chase-butterfly.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-chase-butterfly.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-custom-licking-paw.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-custom-licking-paw.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-custom-petting.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-custom-petting.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-custom-yawning.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-custom-yawning.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-sleeping.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-sleeping.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-sniffing.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-sniffing.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-stretching.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-stretching.webp"),
    },
    BuiltinAsset {
        relative_path: "family/pet-20260520-112213/extension-tongue.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/pet-20260520-112213/extension-tongue.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/identity-base.png",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/identity-base.png"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/spritesheet.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/spritesheet.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/extension-custom-basketball.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/extension-custom-basketball.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/extension-custom-sing.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/extension-custom-sing.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/extension-custom-dance.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/extension-custom-dance.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/extension-custom-rap.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/extension-custom-rap.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/extension-custom-greeting.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/extension-custom-greeting.webp"),
    },
    BuiltinAsset {
        relative_path: "family/ikun_duck/extension-custom-working.webp",
        bytes: include_bytes!("../builtin-runtime/danhuang/family/ikun_duck/extension-custom-working.webp"),
    },
    BuiltinAsset {
        relative_path: "family-references/black-white-dog.jpg",
        bytes: include_bytes!("../builtin-runtime/danhuang/family-references/black-white-dog.jpg"),
    },
    BuiltinAsset {
        relative_path: "family-references/orange-cat-and-hugging-dog.jpg",
        bytes: include_bytes!("../builtin-runtime/danhuang/family-references/orange-cat-and-hugging-dog.jpg"),
    },
];
