from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Calculadora Salario Líquido Uruguay",
    description="<h4>API para calcular el salario líquido en Uruguay considerando aportes BPS e IRPF</h4><h6>(<b>Nota</b>: No se aplica descuento de caja de profesionales)</h4>",
    version="1.0.0",
)

# Valores actualizados para 2025
BPC_2025 = 6576  # Base de Prestaciones y Contribuciones 2024

# Franjas IRPF 2024
FRANJAS_IRPF = [
    {"desde": 0, "hasta": 7, "tasa": 0.0},
    {"desde": 7, "hasta": 10, "tasa": 0.10},
    {"desde": 10, "hasta": 15, "tasa": 0.15},
    {"desde": 15, "hasta": 30, "tasa": 0.24},
    {"desde": 30, "hasta": 50, "tasa": 0.25},
    {"desde": 50, "hasta": 75, "tasa": 0.27},
    {"desde": 75, "hasta": 115, "tasa": 0.31},
    {"desde": 115, "hasta": float("inf"), "tasa": 0.36},
]


# Modelos Pydantic
class SalarioRequest(BaseModel):
    salario_nominal: float = Field(
        ..., gt=23604, description="Salario nominal en pesos uruguayos, debe ser mayor al salario mínimo establecido (UYU 23604)"
    )  # gt = 0 significa que debe ser mayor a 0 (greater than 0)
    hijos_a_cargo: int = Field(
        default=0, ge=0, description="Número de hijos a cargo"
    )  # ge = 0 significa que debe ser mayor o igual a 0 (greater than or equal to 0)
    conyuge_a_cargo: bool = Field(default=False, description="¿Tiene cónyuge a cargo?")
    deducciones_adicionales: float = Field(
        default=0, ge=0, description="Deducciones adicionales mensuales"
    )


class DetalleCalculos(BaseModel):
    salario_nominal: float
    aporte_jubilatorio: float
    aporte_fonasa: float
    aporte_frl: float
    total_aportes_bps: float
    base_irpf: float
    irpf_bruto: float
    deducciones_irpf: float
    irpf_neto: float
    salario_liquido: float
    tasa_fonasa_aplicada: float
    detalle_irpf: list


class SalarioResponse(BaseModel):
    calculos: DetalleCalculos
    porcentaje_descuento_total: float
    bpc_usado: float


def calcular_tasa_fonasa(
    salario_nominal: float, hijos_a_cargo: int, conyuge_a_cargo: bool
) -> float:
    """
    Calcula la tasa de FONASA según las reglas:
    - Salario < 2.5 BPC: tasa reducida
    - Con hijos o cónyuge a cargo: descuentos adicionales
    """
    salario_en_bpc = salario_nominal / BPC_2025

    # Tasa base
    tasa_base = 0.045  # 4.5%

    # Si el salario es menor a 2.5 BPC, hay tasas reducidas
    if salario_en_bpc < 2.5:
        if hijos_a_cargo > 0 or conyuge_a_cargo:
            return 0.03  # 3%
        else:
            return tasa_base  # 4.5% (tasa normal)

    # Para salarios >= 2.5 BPC
    if hijos_a_cargo > 0 or conyuge_a_cargo:
        return tasa_base  # 4.5%
    else:
        return tasa_base  # 4.5%


def calcular_irpf(base_irpf: float) -> tuple[float, list]:
    """
    Calcula el IRPF aplicando las franjas progresivas
    Retorna: (irpf_total, detalle_por_franja)
    """
    irpf_total = 0
    detalle = []
    base_restante = base_irpf

    for franja in FRANJAS_IRPF:
        desde_pesos = franja["desde"] * BPC_2025
        hasta_pesos = (franja["hasta"] * BPC_2025 if franja["hasta"] != float("inf") else float("inf"))

        if base_restante <= 0:
            break

        # Calcular cuánto de esta franja aplica
        if base_irpf > desde_pesos:
            monto_en_franja = min(base_restante, hasta_pesos - desde_pesos)
            if monto_en_franja > 0:
                impuesto_franja = monto_en_franja * franja["tasa"]
                irpf_total += impuesto_franja

                detalle.append(
                    {
                        "franja": f"{franja['desde']} - {franja['hasta']} BPC",
                        "monto_gravado": monto_en_franja,
                        "tasa": franja["tasa"],
                        "impuesto": impuesto_franja,
                    }
                )

                base_restante -= monto_en_franja

    return irpf_total, detalle


def calcular_deducciones_irpf(
    hijos_a_cargo: int, conyuge_a_cargo: bool, deducciones_adicionales: float
) -> float:
    """
    Calcula las deducciones aplicables al IRPF
    """
    deducciones = 0

    # Deducción por hijos (aproximadamente 0.5 BPC por hijo)
    deducciones += hijos_a_cargo * (0.5 * BPC_2025)

    # Deducción por cónyuge (aproximadamente 0.5 BPC)
    if conyuge_a_cargo:
        deducciones += 0.5 * BPC_2025

    # Deducciones adicionales
    deducciones += deducciones_adicionales

    return deducciones


@app.get("/")
async def root():
    return {
        "mensaje": "API Calculadora Salario Líquido Uruguay",
        "version": "1.0.0",
        "valor_bpc": BPC_2025,
        "endpoints": {
            "calcular": "/calcular - POST con datos del salario",
            "info": "/info - GET información de tasas y franjas",
            "docs": "/docs - Documentación interactiva",
            "redoc": "/redoc - Documentación alternativa",
        },
    }


@app.get("/info")
async def obtener_info():
    """Obtiene información sobre las tasas y franjas vigentes"""
    return {
        "valor_bpc": BPC_2025,
        "tasas": {"aporte_jubilatorio": 0.15, "fonasa_base": 0.045, "frl": 0.001},
        "franjas_irpf": [
            {
                "desde_bpc": f["desde"],
                "hasta_bpc": f["hasta"] if f["hasta"] != float("inf") else "sin límite",
                "desde_pesos": f["desde"] * BPC_2025,
                "hasta_pesos": (
                    f["hasta"] * BPC_2025
                    if f["hasta"] != float("inf")
                    else "sin límite"
                ),
                "tasa_porcentual": f"{f['tasa'] * 100}%",
            }
            for f in FRANJAS_IRPF
        ],
    }


@app.post("/calcular", response_model=SalarioResponse)
async def calcular_salario_liquido(datos: SalarioRequest):
    """
    Calcula el salario líquido considerando todos los aportes e impuestos
    """
    try:
        salario_nominal = datos.salario_nominal

        # 1. Calcular aportes a BPS
        aporte_jubilatorio = salario_nominal * 0.15  # 15%

        tasa_fonasa = calcular_tasa_fonasa(
            salario_nominal, datos.hijos_a_cargo, datos.conyuge_a_cargo
        )
        aporte_fonasa = salario_nominal * tasa_fonasa

        aporte_frl = salario_nominal * 0.001  # 0.1%

        total_aportes_bps = aporte_jubilatorio + aporte_fonasa + aporte_frl

        # 2. Calcular base para IRPF
        # Si el salario es mayor a 10 BPC, se incrementa 6% para cálculos IRPF
        salario_en_bpc = salario_nominal / BPC_2025
        if salario_en_bpc > 10:
            base_irpf = salario_nominal * 1.06 - total_aportes_bps
        else:
            base_irpf = salario_nominal - total_aportes_bps

        # 3. Calcular IRPF bruto
        irpf_bruto, detalle_irpf = calcular_irpf(base_irpf)

        # 4. Calcular deducciones IRPF
        deducciones_irpf = calcular_deducciones_irpf(datos.hijos_a_cargo, datos.conyuge_a_cargo, datos.deducciones_adicionales)

        # 5. IRPF neto (no puede ser negativo)
        irpf_neto = max(0, irpf_bruto - deducciones_irpf)

        # 6. Salario líquido final
        salario_liquido = salario_nominal - total_aportes_bps - irpf_neto

        # 7. Porcentaje de descuento total
        porcentaje_descuento = ((salario_nominal - salario_liquido) / salario_nominal) * 100

        detalle_calculos = DetalleCalculos(
            salario_nominal=salario_nominal,
            aporte_jubilatorio=aporte_jubilatorio,
            aporte_fonasa=aporte_fonasa,
            aporte_frl=aporte_frl,
            total_aportes_bps=total_aportes_bps,
            base_irpf=base_irpf,
            irpf_bruto=irpf_bruto,
            deducciones_irpf=deducciones_irpf,
            irpf_neto=irpf_neto,
            salario_liquido=salario_liquido,
            tasa_fonasa_aplicada=tasa_fonasa,
            detalle_irpf=detalle_irpf,
        )

        return SalarioResponse(
            calculos=detalle_calculos,
            porcentaje_descuento_total=round(porcentaje_descuento, 2),
            bpc_usado=BPC_2025,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en el cálculo: {str(e)}")


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bpc_vigente": BPC_2025,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
