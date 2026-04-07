import json
from pathlib import Path

class TeamsConfigManager:
    CONFIG_FILE = Path("teams_config.json")
    
    @classmethod
    def load_config(cls):
        if cls.CONFIG_FILE.is_file():
            try:
                return json.loads(cls.CONFIG_FILE.read_text(encoding="utf-8"))
            except:
                return {"destinations": []}
        return {"destinations": []}

    @classmethod
    def save_config(cls, config):
        try:
            cls.CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
            return True
        except:
            return False

    @classmethod
    def get_destinations(cls):
        """Returns list of dicts: [{'name': 'Dr. House', 'url': '...'}]"""
        config = cls.load_config()
        return config.get("destinations", [])

    @classmethod
    def add_destination(cls, name, url):
        config = cls.load_config()
        dests = config.get("destinations", [])
        # Check duplicate
        for d in dests:
            if d["name"].lower() == name.lower():
                return False, "Ya existe un destino con ese nombre."
        
        dests.append({"name": name, "url": url})
        config["destinations"] = dests
        cls.save_config(config)
        return True, "Guardado correctamente."

    @classmethod
    def delete_destination(cls, index):
        config = cls.load_config()
        dests = config.get("destinations", [])
        if 0 <= index < len(dests):
            del dests[index]
            config["destinations"] = dests
            cls.save_config(config)
            return True
        return False
