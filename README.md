# Installation
```
git clone https://github.com/fgaurat/amazon_products_csv.git

cd amazon_products_csv
pip install -r requirements.txt
```
## Configuration
Dans le fichier config.ini, renseigner les informations (api_key,...).
Il est possible de faire plusieurs fichier de configuration.
ex:
```
[CONFIG]
product_query=Portefeuille EDC
associate_id=affiliate_id
rainforest_api_key=xxxxxx
number_of_pages=1
amazon_domain=amazon.fr
```

## Usage
```
python main.py config.ini
```

## Output
En sortie, le fichier csv portera le nom de product_query.

