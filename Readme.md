
# PI MLOps: Modelo de recomendación

**Objetivos**:
1. Implementar una API de consultas en Render para permitir el acceso a datos y funcionalidades específicas.
2. Construir un modelo de recomendación utilizando relaciones de item-item y usuario-item para ofrecer recomendaciones personalizadas a los usuarios de Steam.
3. Trabajar con archivos JSON comprimidos proporcionados por Steam, que pueden contener datos anidados y faltantes, así como otras dificultades, que resolveremos mediante procesos de Extracción, Transformación y Carga (ETL) y Análisis Exploratorio de Datos (EDA).

<img src="_src/steam.jpg">

## API Referencias

#### Consulta 1: Obtener la cantidad total de juegos vendidos y gratis por año de un desarrollador

```http
  GET /developer/{desarrollador}
```
| Parametro | Formato     | Descripción                |
| :-------- | :------- | :------------------------- |
| `Desarrollador` | `string` | Recibe el nombre del desarrollador |

#### Consulta 2: Obtener los USD gastados,cantidad de juegos,porcentaje de recomendación por usuario
```http
  GET /userdata/{user_id}
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `usuario`      | `string` | Recibe el nombre del usuario |

#### Consulta 3: Obtener al usuario con mas horas en el genero y con cantidad de horas por año
```http
  GET /userforgenre/{genero}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `genero`      | `string` | Recibe el nombre del genero |

#### Consulta 4: Obtener los mejores 3 desarrolladores por año
```http
  GET /best_developer_year/{year}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `year`      | `int` | Recibe el numero del año |

#### Consulta 5: Obtener los comentarios positivos y negativos del desarrolador
```http
  GET /developer_reviews_analysis/{Desarrollador}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `Desarrollador`      | `string` | recibe el nombre del desarrollador |



## Tecnologias Utilizadas

**Manipulación de Datos** 
- ![Pandas](https://img.shields.io/badge/-Pandas-333333?style=flat&logo=pandas)
- ![Numpy](https://img.shields.io/badge/-Numpy-333333?style=flat&logo=numpy)

**Visualización** 
- ![Matplotlib](https://img.shields.io/badge/-Matplotlib-333333?style=flat&logo=matplotlib)
- ![Seaborn](https://img.shields.io/badge/-Seaborn-333333?style=flat&logo=seaborn)

**Machine Learning** 
- ![Scikitlearn](https://img.shields.io/badge/scikit--learn-333333?style=flat&logo=scikit-learn)
- ![Scikitlearn](https://img.shields.io/badge/NLTK-333333?style=flat&logo=nltk)

**Despliegue de aplicaciones**
- ![Renderizar](https://img.shields.io/badge/-Render-333333?style=flat&logo=render)
- ![FastAPI](https://img.shields.io/badge/-FastAPI-333333?style=flat&logo=fastapi)

# Contacto

Puedes contactarme a través de los siguientes medios:

| [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maxi-lizarraga)|[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MaxiLizarraga) | | 
| --- | --- | --- |

### Email : maxijavierlizarraga@outlook.com