import json
from datetime import datetime
from typing import List, Optional

class ReservoirData:
    def __init__(
        self,
        dato_Id: str,
        omrType: str,
        omrnr: int,
        iso_aar: int,
        iso_uke: int,
        fyllingsgrad: float,
        kapasitet_TWh: float,
        fylling_TWh: float,
        neste_Publiseringsdato: Optional[str],
        fyllingsgrad_forrige_uke: Optional[float],
        endring_fyllingsgrad: Optional[float],
    ):
        self.dato_Id = dato_Id
        self.omrType = omrType
        self.omrnr = omrnr
        self.iso_aar = iso_aar
        self.iso_uke = iso_uke
        self.fyllingsgrad = fyllingsgrad
        self.kapasitet_TWh = kapasitet_TWh
        self.fylling_TWh = fylling_TWh
        self.neste_Publiseringsdato = (
            datetime.fromisoformat(neste_Publiseringsdato)
            if neste_Publiseringsdato and neste_Publiseringsdato != "0001-01-01T00:00:00"
            else None
        )
        self.fyllingsgrad_forrige_uke = fyllingsgrad_forrige_uke
        self.endring_fyllingsgrad = endring_fyllingsgrad

    def __repr__(self):
        return (
            f"ReservoirData(dato_Id={self.dato_Id}, omrType={self.omrType}, omrnr={self.omrnr}, "
            f"iso_aar={self.iso_aar}, iso_uke={self.iso_uke}, fyllingsgrad={self.fyllingsgrad}, "
            f"kapasitet_TWh={self.kapasitet_TWh}, fylling_TWh={self.fylling_TWh}, "
            f"neste_Publiseringsdato={self.neste_Publiseringsdato}, "
            f"fyllingsgrad_forrige_uke={self.fyllingsgrad_forrige_uke}, "
            f"endring_fyllingsgrad={self.endring_fyllingsgrad})"
        )

def parse_reservoir_data(json_data: str) -> List[ReservoirData]:
    data = json.loads(json_data)
    return [
        ReservoirData(
            dato_Id=item["dato_Id"],
            omrType=item["omrType"],
            omrnr=item["omrnr"],
            iso_aar=item["iso_aar"],
            iso_uke=item["iso_uke"],
            fyllingsgrad=item["fyllingsgrad"],
            kapasitet_TWh=item["kapasitet_TWh"],
            fylling_TWh=item["fylling_TWh"],
            neste_Publiseringsdato=item.get("neste_Publiseringsdato"),
            fyllingsgrad_forrige_uke=item.get("fyllingsgrad_forrige_uke"),
            endring_fyllingsgrad=item.get("endring_fyllingsgrad"),
        )
        for item in data
    ]

if __name__ == "__main__":
    # Example usage
    example_json = """[{
        "dato_Id": "2025-10-19",
        "omrType": "VASS",
        "omrnr": 3,
        "iso_aar": 2025,
        "iso_uke": 42,
        "fyllingsgrad": 0.9478293,
        "kapasitet_TWh": 28.155403,
        "fylling_TWh": 26.686516,
        "neste_Publiseringsdato": "2025-10-29T13:00:00",
        "fyllingsgrad_forrige_uke": 0.9363148,
        "endring_fyllingsgrad": 0.011514485
    }]"""

    parsed_data = parse_reservoir_data(example_json)
    for reservoir in parsed_data:
        print(reservoir)