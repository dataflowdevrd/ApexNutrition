import uuid
import os
import requests
from typing import Tuple
from .models import VentaCreate, TipoNCF, DeliveryQuoteResponse

class BillingService:
    ITBIS_RATE = 0.18  # Tasa oficial 18%

    @staticmethod
    def generar_secuencia_ncf(tipo: TipoNCF, secuencia_actual: int) -> str:
        """Formatea el comprobante de acuerdo a la DGII (Letra + Tipo + 8 dígitos)."""
        return f"{tipo.value}{secuencia_actual:08d}"

    @classmethod
    def calcular_totales(cls, venta_data: VentaCreate) -> Tuple[float, float, float]:
        """Calcula Subtotal, ITBIS y Monto Total."""
        subtotal = sum(item.cantidad * item.precio_unitario for item in venta_data.items)
        itbis = round(subtotal * cls.ITBIS_RATE, 2) if venta_data.aplica_itbis else 0.0
        total = round(subtotal + itbis, 2)
        return round(subtotal, 2), itbis, total

class DeliveryService:
    TARIFA_BASE_DOP = 150.00    # Tarifa inicial para los primeros 3 km
    COSTO_POR_KM_EXTRA = 35.00  # Costo por kilómetro adicional
    KM_BASE = 3.0

    @classmethod
    def calcular_tarifa_envio(cls, distancia_km: float) -> float:
        """Calcula el costo de entrega en base a la distancia en km."""
        if distancia_km <= cls.KM_BASE:
            return cls.TARIFA_BASE_DOP
        km_adicionales = distancia_km - cls.KM_BASE
        costo_total = cls.TARIFA_BASE_DOP + (km_adicionales * cls.COSTO_POR_KM_EXTRA)
        return round(costo_total, 2)

    @classmethod
    def cotizar_ruta(cls, destino_lat: float, destino_lng: float, origen_lat=None, origen_lng=None) -> DeliveryQuoteResponse:
        api_key = os.getenv("OPENROUTESERVICE_API_KEY")
        configured_origin = (os.getenv("ROUTE_ORIGIN_LAT"), os.getenv("ROUTE_ORIGIN_LNG"))
        origin = (
            origen_lat if origen_lat is not None else configured_origin[0],
            origen_lng if origen_lng is not None else configured_origin[1],
        )
        if None in origin or "" in origin:
            raise ValueError("Configura ROUTE_ORIGIN_LAT/LNG para cotizar la ruta")

        coordinates = [[float(origin[1]), float(origin[0])], [destino_lng, destino_lat]]
        if api_key:
            response = requests.post(
                "https://api.openrouteservice.org/v2/directions/driving-car",
                headers={"Authorization": api_key, "Content-Type": "application/json"},
                json={"coordinates": coordinates, "instructions": False},
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
            summary = payload["routes"][0]["summary"]
            distance_km = round(summary["distance"] / 1000, 2)
            duration_minutes = round(summary["duration"] / 60)
            provider = "openrouteservice"
        else:
            response = requests.get(
                f"https://router.project-osrm.org/route/v1/driving/{coordinates[0][0]},{coordinates[0][1]};{coordinates[1][0]},{coordinates[1][1]}",
                params={"overview": "false"},
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
            route = payload.get("routes", [{}])[0]
            if payload.get("code") != "Ok" or not route:
                raise ValueError("OSRM no pudo calcular una ruta para esta ubicación")
            distance_km = round(route["distance"] / 1000, 2)
            duration_minutes = round(route["duration"] / 60)
            provider = "OSRM / OpenStreetMap"

        return DeliveryQuoteResponse(
            distancia_km=distance_km,
            duracion_minutos=duration_minutes,
            costo_envio_dop=cls.calcular_tarifa_envio(distance_km),
            proveedor=provider,
        )