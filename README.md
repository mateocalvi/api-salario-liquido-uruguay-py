# 💰 API Calculadora Salario Líquido Uruguay

Una API REST completa y actualizada para calcular el salario líquido en Uruguay, considerando todos los aportes BPS e IRPF vigentes para 2025.

## 🌐 API en Vivo

**URL Base:** `https://api-salario-liquido-uy.onrender.com`

**Documentación Interactiva:**
- 📚 Swagger UI: [https://api-salario-liquido-uy.onrender.com/docs](https://api-salario-liquido-uy.onrender.com/docs)
- 📖 ReDoc: [https://api-salario-liquido-uy.onrender.com/redoc](https://api-salario-liquido-uy.onrender.com/redoc)

## 🎯 ¿Por qué esta API?

Los simuladores oficiales de BPS y DGI tienen varios problemas:
- No manejan correctamente las franjas del FONASA
- Cálculos incorrectos en casos específicos
- Interfaces poco amigables para desarrolladores
- No están actualizados regularmente

Esta API soluciona todos estos problemas y está **✅ actualizada para 2025** con el nuevo valor de BPC.

## 🚀 Uso Rápido

### Ejemplo básico con curl:
```bash
curl -X POST "https://api-salario-liquido-uy.onrender.com/calcular" \
     -H "Content-Type: application/json" \
     -d '{
       "salario_nominal": 85000,
       "hijos_a_cargo": 1,
       "conyuge_a_cargo": false,
       "deducciones_adicionales": 0
     }'
```

### Ejemplo con Python:
```python
import requests

datos = {
    "salario_nominal": 85000,
    "hijos_a_cargo": 1,
    "conyuge_a_cargo": True,
    "deducciones_adicionales": 5000
}

response = requests.post(
    "https://api-salario-liquido-uy.onrender.com/calcular",
    json=datos
)

resultado = response.json()
print(f"Salario líquido: ${resultado['calculos']['salario_liquido']:,.0f}")
```

### Ejemplo con JavaScript:
```javascript
const calcularSalario = async () => {
    const response = await fetch('https://api-salario-liquido-uy.onrender.com/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            salario_nominal: 85000,
            hijos_a_cargo: 2,
            conyuge_a_cargo: false,
            deducciones_adicionales: 3000
        })
    });

    const data = await response.json();
    console.log(`Salario líquido: $${data.calculos.salario_liquido.toLocaleString()}`);
};
```

## 📋 Endpoints Disponibles

### `GET /`
Información general de la API y endpoints disponibles.

**Response:**
```json
{
  "mensaje": "API Calculadora Salario Líquido Uruguay",
  "version": "1.0.0",
  "bpc_2025": 6576,
  "endpoints": {
    "calcular": "/calcular - POST con datos del salario",
    "info": "/info - GET información de tasas y franjas"
  }
}
```

### `GET /info`
Obtiene información detallada sobre tasas y franjas vigentes.

**Response:**
```json
{
  "bpc_2025": 6576,
  "tasas": {
    "aporte_jubilatorio": 0.15,
    "fonasa_base": 0.045,
    "frl": 0.001
  },
  "franjas_irpf": [
    {
      "desde_bpc": 0,
      "hasta_bpc": 7,
      "desde_pesos": 0,
      "hasta_pesos": 46032,
      "tasa_porcentual": "0.0%"
    },
    {
      "desde_bpc": 7,
      "hasta_bpc": 10,
      "desde_pesos": 46032,
      "hasta_pesos": 65760,
      "tasa_porcentual": "10.0%"
    }
    // ... más franjas
  ]
}
```

### `GET /health`
Endpoint de health check para monitoreo.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-04T15:30:00.000Z",
  "bpc_vigente": 6576
}
```

### `POST /calcular`
**El endpoint principal** - Calcula el salario líquido con todos los detalles.

#### Request Body:
```json
{
  "salario_nominal": 85000,
  "hijos_a_cargo": 2,
  "conyuge_a_cargo": true,
  "deducciones_adicionales": 5000
}
```

#### Parámetros:

| Campo                     | Tipo    | Requerido | Descripción                                       |
| ------------------------- | ------- | --------- | ------------------------------------------------- |
| `salario_nominal`         | number  | ✅         | Salario nominal en pesos uruguayos (debe ser > 0) |
| `hijos_a_cargo`           | integer | ❌         | Número de hijos a cargo (default: 0)              |
| `conyuge_a_cargo`         | boolean | ❌         | ¿Tiene cónyuge a cargo? (default: false)          |
| `deducciones_adicionales` | number  | ❌         | Deducciones adicionales mensuales (default: 0)    |

#### Response:
```json
{
  "calculos": {
    "salario_nominal": 85000,
    "aporte_jubilatorio": 12750,
    "aporte_fonasa": 3825,
    "aporte_frl": 85,
    "total_aportes_bps": 16660,
    "base_irpf": 72588,
    "irpf_bruto": 2134.8,
    "deducciones_irpf": 6576,
    "irpf_neto": 0,
    "salario_liquido": 68340,
    "tasa_fonasa_aplicada": 0.045,
    "detalle_irpf": [
      {
        "franja": "0 - 7 BPC",
        "monto_gravado": 46032,
        "tasa": 0,
        "impuesto": 0
      },
      {
        "franja": "7 - 10 BPC",
        "monto_gravado": 19728,
        "tasa": 0.10,
        "impuesto": 1972.8
      }
    ]
  },
  "porcentaje_descuento_total": 19.6,
  "bpc_usado": 6576
}
```

#### Descripción de Campos de Response:

| Campo                        | Descripción                                                   |
| ---------------------------- | ------------------------------------------------------------- |
| `salario_nominal`            | Salario bruto mensual antes de descuentos                     |
| `aporte_jubilatorio`         | 15% del salario - va a tu futura jubilación                   |
| `aporte_fonasa`              | 3-4.5% del salario - financia salud pública                   |
| `aporte_frl`                 | 0.1% del salario - fondo reconversión laboral                 |
| `total_aportes_bps`          | Suma de todos los aportes BPS                                 |
| `base_irpf`                  | Base para calcular IRPF (con incremento ficto si corresponde) |
| `irpf_bruto`                 | IRPF antes de deducciones                                     |
| `deducciones_irpf`           | Deducciones por hijos, cónyuge, etc.                          |
| `irpf_neto`                  | IRPF final a pagar                                            |
| `salario_liquido`            | **Dinero que efectivamente cobras**                           |
| `tasa_fonasa_aplicada`       | Tasa FONASA usada (varía por situación familiar)              |
| `detalle_irpf`               | Desglose por franjas del IRPF                                 |
| `porcentaje_descuento_total` | % total descontado del salario bruto                          |
| `bpc_usado`                  | Valor BPC usado en cálculos (2025: $6,576)                    |

## 🔧 Instalación Local

Si quieres ejecutar la API en tu computadora:

### Prerrequisitos:
- Python 3.8+
- pip

### Pasos:

1. **Clonar/descargar archivos**
```bash
mkdir salario-liquido-api
cd salario-liquido-api
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install fastapi uvicorn pydantic
```

4. **Ejecutar**
```bash
python main.py
```

5. **Acceder**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 🌟 Características

- ✅ **Actualizado 2025** - BPC $6,576
- ✅ **Cálculos precisos** - Incluye todos los casos especiales
- ✅ **FONASA variable** - Tasas correctas según situación familiar
- ✅ **IRPF progresivo** - Franjas aplicadas correctamente
- ✅ **Incremento ficto** - Para salarios > 10 BPC
- ✅ **Deducciones** - Hijos, cónyuge, adicionales
- ✅ **Validaciones** - Inputs validados con Pydantic
- ✅ **Documentación automática** - Swagger UI y ReDoc
- ✅ **Detalle completo** - Desglose por franjas del IRPF
- ✅ **API REST** - Fácil integración en cualquier aplicación

## 🔍 Casos de Uso

### 💼 Para Desarrolladores
- Integrar cálculo de salarios en sistemas de RRHH
- Apps móviles de finanzas personales
- Calculadoras web personalizadas
- Sistemas de nómina

### 👤 Para Particulares
- Calcular tu salario líquido real
- Comparar ofertas de trabajo
- Planificar finanzas personales
- Entender tus descuentos

### 🏢 Para Empresas
- Mostrar salario líquido en ofertas de empleo
- Calculadoras internas para empleados
- Sistemas de simulación salarial

## 📞 Soporte y Errores

Si encuentras errores en los cálculos o tienes sugerencias:

1. **Issues:** Reporta problemas con ejemplos específicos
2. **Validación:** Compara con recibos de sueldo reales
3. **Actualizaciones:** Los valores se actualizan cuando cambian las normativas

## 🏗️ Arquitectura Técnica

- **Framework:** FastAPI (Python)
- **Validación:** Pydantic
- **Documentación:** OpenAPI/Swagger automática
- **Hosting:** Render (plan gratuito)
- **Performance:** ~100ms por cálculo
- **Disponibilidad:** 99%+ uptime

## 📈 Cambios 2025

### Actualizaciones principales:
- **BPC 2025:** $6,576 (+6.5% vs 2024)
- **Franjas IRPF actualizadas:** Nuevos montos en pesos
- **Deducciones incrementadas:** Proporcionales al nuevo BPC
- **Umbral 10 BPC:** Ahora $65,760 (vs $61,770 en 2024)

### Impacto en salarios típicos:
- **$50,000:** Salario líquido similar (franjas bajas)
- **$80,000:** Leve reducción IRPF (umbral más alto)
- **$120,000+:** Mayor ahorro por deducciones incrementadas

---

## 💡 Conceptos Importantes

### 🏛️ Aportes BPS (Obligatorios)

#### 1. Aporte Jubilatorio (15%)
- Tu "ahorro forzoso" para la jubilación
- Va a tu cuenta individual en BPS
- **No se pierde** - es tu dinero para el futuro

#### 2. FONASA (3% - 4.5%)
- Financia el sistema de salud público
- Tasa variable según salario y cargas familiares:
  - **< 2.5 BPC con familia:** 3%
  - **≥ 2.5 BPC:** 4.5%

#### 3. FRL (0.1%)
- Fondo de Reconversión Laboral
- Financia programas de capacitación para desempleados

### 📊 IRPF - Sistema Progresivo (¡Importante!)

**❌ Error común:** "Si gano $100,000 y caigo en la franja del 24%, pago 24% sobre todo mi salario"

**✅ Realidad:** El IRPF es progresivo - cada franja tiene su tasa:

| Desde    | Hasta   | Tasa | En Pesos (2025)     |
| -------- | ------- | ---- | ------------------- |
| 0 BPC    | 7 BPC   | 0%   | $0 - $46,032        |
| 7 BPC    | 10 BPC  | 10%  | $46,032 - $65,760   |
| 10 BPC   | 15 BPC  | 15%  | $65,760 - $98,640   |
| 15 BPC   | 30 BPC  | 24%  | $98,640 - $197,280  |
| 30 BPC   | 50 BPC  | 25%  | $197,280 - $328,800 |
| 50 BPC   | 75 BPC  | 27%  | $328,800 - $493,200 |
| 75 BPC   | 115 BPC | 31%  | $493,200 - $756,240 |
| 115+ BPC | ∞       | 36%  | $756,240+           |

**Ejemplo:** Con $100,000 de salario (2025):
- 0% sobre primeros $46,032 = $0
- 10% sobre siguientes $19,728 = $1,973
- 15% sobre los $34,240 restantes = $5,136
- **Total IRPF = $7,109** (no $24,000!)

### 🔢 Incremento Ficto del 6%

Si tu salario > 10 BPC (~$65,760):
- Se suma 6% **solo para calcular el IRPF**
- Tu salario real no cambia
- Ejemplo: $85,000 → se usa $90,100 para calcular impuesto

### 💳 Deducciones IRPF

Reducen el impuesto a pagar:
- **Hijos a cargo:** ~$3,288 por hijo (~0.5 BPC)
- **Cónyuge a cargo:** ~$3,288 (~0.5 BPC)
- **Gastos médicos, educativos, etc.**

### 📏 BPC (Base de Prestaciones y Contribuciones)

- **2025:** $6,576
- Unidad de medida que se actualiza anualmente
- Todas las franjas se definen en BPC para ajustarse con inflación
- **Incremento 2024→2025:** 6.5% (+$399)

---

## 📄 Licencia

Este proyecto está basado en el trabajo de [ismaelpadilla/salario-liquido-uruguay](https://github.com/ismaelpadilla/salario-liquido-uruguay) y busca proporcionar una API REST moderna y confiable para cálculos salariales en Uruguay.

---

**⭐ ¿Te resulta útil?** ¡Compártela con otros desarrolladores uruguayos!

**🐛 ¿Encontraste un error?** Reporta el issue con un ejemplo específico.

**💡 ¿Tienes una mejora?** ¡Los pull requests son bienvenidos!

**🔄 Última actualización:** Agosto 2025 - BPC $6,576
