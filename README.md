# Installation
```
git clone https://github.com/fgaurat/amazon_products_csv.git

cd amazon_products_csv
python3 -m venv .venv

# pour windows
.venv/Scripts/activate.bat

# pour linux/macos
source .venv/bin/activate

pip install -r requirements.txt
```
## Configuration
Dans le fichier config.yml, renseigner les informations (api_key,...).
Il est possible de faire plusieurs fichier de configuration.
ex:
```
product_queries:
  - product 01
  - product 02
  - product 03
associate_id: 
rainforest_api_key: 
number_of_pages: 1
amazon_domain: amazon.fr

```

## Usage
```
python main.py config.yml
```

## Output
En sortie, le fichier csv portera le nom de product_query.

