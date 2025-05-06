import os
from enum import EnumType

import httpx
from dotenv import load_dotenv

load_dotenv()


class TypeChampionship(EnumType):
    GP = "gp"
    CUP = "cup"


class APIGetter:
    def __init__(self):
        self.url = os.environ.get("G_CUP_URL")
        self.api_key = os.environ.get("G_CUP_API_KEY")

    def get_data_championships(
        self,
        champ_type: TypeChampionship = "gp",
        from_year: int | None = None,
        to_year: int | None = None,
    ):
        url = f"{self.url}/championships/list"
        response = httpx.get(
            url,
            params={
                "signature": self.api_key,
                "types": champ_type,
                "fromYear": from_year,
                "toYear": to_year,
            },
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def get_data_championships_by_id(
        self, champ_id: int, champ_type: TypeChampionship = "gp"
    ):
        url = f"{self.url}/championships/get"
        response = httpx.get(
            url,
            params={
                "signature": self.api_key,
                "id": champ_id,
                "type": champ_type,
            },
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def data_stage(
        self, stage_id: int, stage_type: TypeChampionship = "gp"
    ) -> {dict | None}:
        """Получает данные по этапам чемпионата"""
        url = f"{self.url}/stages/get?id=&type="
        response = httpx.get(
            url,
            params={
                "signature": self.api_key,
                "id": stage_id,
                "type": stage_type,
            },
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {}


if __name__ == "__main__":
    g_cup = APIGetter()
    championships = g_cup.get_data_championships(from_year=2021, to_year=2023)
    for champ in championships:
        cham_data = g_cup.get_data_championships_by_id(champ["id"])
        for stage in cham_data["stages"]:
            stage_data = g_cup.data_stage(stage["id"])
            print(stage_data)
