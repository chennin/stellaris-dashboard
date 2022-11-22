import json
import logging

logger = logging.getLogger(__name__)


class NameRenderer:
    default_name = "Unknown name"

    def __init__(self, localization_files):
        self.localization_files = localization_files
        self.name_mapping = None

    def load_name_mapping(self):
        """
        Load a mapping of all name keys to their corresponding templates / localized values.

        Localization files can be passed in, by default the dashboard tries to locate them from
        """
        self.name_mapping = {"global_event_country": "Global event country"}
        for p in self.localization_files:
            # manually parse yaml, yaml.safe_load doesnt seem to work
            with open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    try:
                        key, val, *rest = line.strip().split('"')
                        self.name_mapping[key.strip().rstrip(":0")] = val.strip()
                    except Exception:
                        pass

    def render_from_json(self, name_json: str):
        try:
            json_dict = json.loads(name_json)
        except (json.JSONDecodeError, TypeError):
            return str(name_json)
        rendered = self.render_from_dict(json_dict)
        if rendered == self.default_name:
            logger.warning(
                "Failed to resolve a name, please check if you configured localization files."
            )
            logger.warning(f"Instructions can be found in README.md")
            logger.warning(f"Failed name: {name_json!r}")
        return rendered

    def render_from_dict(self, name_dict: dict) -> str:
        if not isinstance(name_dict, dict):
            logger.warning(f"Expected name template dictionary, received {name_dict}")
            return str(name_dict)

        key = name_dict.get("key", self.default_name)
        if name_dict.get("literal") == "yes":
            return key

        render_template = self.name_mapping.get(key, key)

        substitution_values = []
        if "value" in name_dict:
            return self.render_from_dict(name_dict["value"])

        for var in name_dict.get("variables", []):
            if "key" not in var or "value" not in var:
                continue
            var_key = var.get("key")
            substitution_values.append((var_key, self.render_from_dict(var["value"])))

        # try all combinations of escaping identifiers to substitute the variables
        for subst_key, subst_value in substitution_values:
            for lparen, rparen in [
                ("<", ">"),
                ("[", "]"),
                ("$", "$"),
            ]:
                render_template = render_template.replace(
                    f"{lparen}{subst_key}{rparen}", subst_value
                )
        return render_template


global_renderer: NameRenderer = None


def render_name(json_str: str):
    global global_renderer
    if global_renderer is None:
        from stellarisdashboard import config

        global_renderer = NameRenderer(config.CONFIG.localization_files)
        global_renderer.load_name_mapping()
    return global_renderer.render_from_json(json_str)


COLONIZABLE_PLANET_CLASSES_PLANETS = {
    "pc_desert",
    "pc_arid",
    "pc_savannah",
    "pc_tropical",
    "pc_continental",
    "pc_ocean",
    "pc_tundra",
    "pc_arctic",
    "pc_alpine",
    "pc_gaia",
    "pc_nuked",
    "pc_machine",
}
COLONIZABLE_PLANET_CLASSES_MEGA_STRUCTURES = {
    "pc_ringworld_habitable",
    "pc_habitat",
}

# Planet classes for the planetary diversity mod
# (see https://steamcommunity.com/workshop/filedetails/discussion/1466534202/3397295779078104093/)
COLONIZABLE_PLANET_CLASSES_PD_PLANETS = {
    "pc_antarctic",
    "pc_deadcity",
    "pc_retinal",
    "pc_irradiated_terrestrial",
    "pc_lush",
    "pc_geocrystalline",
    "pc_marginal",
    "pc_irradiated_marginal",
    "pc_marginal_cold",
    "pc_crystal",
    "pc_floating",
    "pc_graveyard",
    "pc_mushroom",
    "pc_city",
    "pc_archive",
    "pc_biolumen",
    "pc_technoorganic",
    "pc_tidallylocked",
    "pc_glacial",
    "pc_frozen_desert",
    "pc_steppe",
    "pc_hadesert",
    "pc_boreal",
    "pc_sandsea",
    "pc_subarctic",
    "pc_geothermal",
    "pc_cascadian",
    "pc_swamp",
    "pc_mangrove",
    "pc_desertislands",
    "pc_mesa",
    "pc_oasis",
    "pc_hajungle",
    "pc_methane",
    "pc_ammonia",
}
COLONIZABLE_PLANET_CLASSES = (
    COLONIZABLE_PLANET_CLASSES_PLANETS
    | COLONIZABLE_PLANET_CLASSES_MEGA_STRUCTURES
    | COLONIZABLE_PLANET_CLASSES_PD_PLANETS
)

DESTROYED_BY_WEAPONS_PLANET_CLASSES = {
    "pc_shattered",
    "pc_shielded",
    "pc_ringworld_shielded",
    "pc_habitat_shielded",
    "pc_ringworld_habitable_damaged",
}
DESTROYED_BY_EVENTS_AND_CRISES_PLANET_CLASSES = {
    "pc_egg_cracked",
    "pc_shrouded",
    "pc_ai",
    "pc_infested",
    "pc_gray_goo",
}
DESTROYED_PLANET_CLASSES = (
    DESTROYED_BY_WEAPONS_PLANET_CLASSES | DESTROYED_BY_EVENTS_AND_CRISES_PLANET_CLASSES
)


def is_destroyed_planet(planet_class):
    return planet_class in DESTROYED_PLANET_CLASSES


def is_colonizable_planet(planet_class):
    return planet_class in COLONIZABLE_PLANET_CLASSES


def is_colonizable_megastructure(planet_class):
    return planet_class in COLONIZABLE_PLANET_CLASSES_MEGA_STRUCTURES


LOWERCASE_WORDS = {"the", "in", "of", "for", "is", "over", "under"}
WORD_REPLACEMENT = {
    "Ai": "AI",
    "Ftl": "FTL",
    "Tb": "Tile Blocker",
}


def convert_id_to_name(object_id: str, remove_prefix="") -> str:
    words = [word for word in object_id.split("_") if word != remove_prefix]
    words = [
        word.capitalize() if word not in LOWERCASE_WORDS else word for word in words
    ]
    words = [WORD_REPLACEMENT.get(word, word) for word in words]
    return " ".join(words)

# map colors from colors.txt in 3.5.3
COLORS = {
    "beige": { "r": 150, "g": 126, "b": 90 },
    "black": { "r": 27, "g": 27, "b": 27 },
    "blue": { "r": 46, "g": 63, "b": 153 },
    "bright_purple": { "r": 194, "g": 125, "b": 227 },
    "bright_yellow": { "r": 224, "g": 214, "b": 46 },
    "brown": { "r": 156, "g": 91, "b": 45 },
    "burgundy": { "r": 89, "g": 18, "b": 39 },
    "cerise_red": { "r": 245, "g": 102, "b": 102 },
    "cloud_purple": { "r": 167, "g": 58, "b": 217 },
    "dark_blue": { "r": 45, "g": 61, "b": 116 },
    "dark_brown": { "r": 107, "g": 68, "b": 40 },
    "dark_green": { "r": 27, "g": 66, "b": 26 },
    "dark_grey": { "r": 62, "g": 62, "b": 62 },
    "dark_orange": { "r": 167, "g": 57, "b": 0 },
    "dark_purple": { "r": 81, "g": 15, "b": 113 },
    "dark_red": { "r": 103, "g": 25, "b": 39 },
    "dark_steel": { "r": 76, "g": 90, "b": 98 },
    "dark_teal": { "r": 51, "g": 127, "b": 91 },
    "desert_yellow": { "r": 237, "g": 231, "b": 116 },
    "faded_blue": { "r": 191, "g": 187, "b": 224 },
    "frog_green": { "r": 209, "g": 241, "b": 126 },
    "green": { "r": 46, "g": 102, "b": 41 },
    "grey": { "r": 128, "g": 128, "b": 128 },
    "hard_steel": { "r": 152, "g": 168, "b": 173 },
    "ice_turquoise": { "r": 137, "g": 237, "b": 236 },
    "indigo": { "r": 36, "g": 21, "b": 156 },
    "intense_blue": { "r": 30, "g": 159, "b": 220 },
    "intense_burgundy": { "r": 149, "g": 20, "b": 72 },
    "intense_orange": { "r": 255, "g": 86, "b": 0 },
    "intense_pink": { "r": 190, "g": 40, "b": 134 },
    "intense_purple": { "r": 139, "g": 39, "b": 184 },
    "intense_red": { "r": 241, "g": 37, "b": 15 },
    "intense_turquoise": { "r": 55, "g": 178, "b": 170 },
    "khaki_brown": { "r": 174, "g": 121, "b": 83 },
    "light_blue": { "r": 71, "g": 114, "b": 178 },
    "light_green": { "r": 160, "g": 222, "b": 141 },
    "light_grey": { "r": 191, "g": 191, "b": 191 },
    "light_indigo": { "r": 96, "g": 82, "b": 207 },
    "light_orange": { "r": 244, "g": 139, "b": 15 },
    "light_pink": { "r": 222, "g": 64, "b": 163 },
    "light_turquoise": { "r": 23, "g": 98, "b": 98 },
    "medium_steel": { "r": 101, "g": 119, "b": 128 },
    "mist_blue": { "r": 137, "g": 221, "b": 246 },
    "moss_green": { "r": 112, "g": 142, "b": 35 },
    "ocean_turquoise": { "r": 49, "g": 208, "b": 198 },
    "ochre_brown": { "r": 224, "g": 197, "b": 106 },
    "off_white": { "r": 239, "g": 239, "b": 239 },
    "orange": { "r": 237, "g": 118, "b": 25 },
    "pink_purple": { "r": 221, "g": 216, "b": 254 },
    "pink": { "r": 151, "g": 15, "b": 100 },
    "pink_red": { "r": 237, "g": 131, "b": 131 },
    "purple": { "r": 109, "g": 24, "b": 150 },
    "red_orange": { "r": 224, "g": 64, "b": 64 },
    "red": { "r": 151, "g": 14, "b": 18 },
    "satin_burgundy": { "r": 116, "g": 31, "b": 65 },
    "shadow_blue": { "r": 15, "g": 17, "b": 91 },
    "shadow_green": { "r": 32, "g": 55, "b": 41 },
    "shadow_purple": { "r": 63, "g": 9, "b": 89 },
    "shadow_steel": { "r": 51, "g": 60, "b": 65 },
    "shadow_teal": { "r": 9, "g": 57, "b": 57 },
    "ship_steel": { "r": 131, "g": 150, "b": 156 },
    "sick_green": { "r": 157, "g": 175, "b": 35 },
    "silver_steel": { "r": 208, "g": 225, "b": 230 },
    "sky_blue": { "r": 88, "g": 188, "b": 235 },
    "sun_green": { "r": 230, "g": 244, "b": 147 },
    "swamp_green": { "r": 88, "g": 107, "b": 39 },
    "teal": { "r": 76, "g": 153, "b": 84 },
    "toxic_green": { "r": 168, "g": 218, "b": 39 },
    "turquoise": { "r": 61, "g": 153, "b": 147 },
    "wave_blue": { "r": 159, "g": 151, "b": 224 },
    "white": { "r": 255, "g": 255, "b": 255 },
    "yellow": { "r": 204, "g": 148, "b": 41 },
}
