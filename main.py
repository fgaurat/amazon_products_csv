#!/usr/bin/env python
import argparse
import asyncio
import httpx
import os
import sys
import yaml
import time
import json
import pandas as pd
from utils import slugify
from pprint import pprint
import configparser
from tqdm import tqdm
import ast

# rainforest_api_key = "CBE53E33495B444983FCCF9DA8BA42A2"

default_row = {
    "ID produit": "",
    "Référence du produit (AmazonID)": "",
    "Référence": "",
    "Nom du produit": "",
    "Description courte": "",
    "Description longue": "",
    "Mots clés": "",
    "Caractéristiques": "",
    "Poids": "",
    "Nombre de produits en stock": "",
    "Titre de la page": "",
    "URL (sans .html)": "",
    "Méta description": "",
    "Lien d'affiliation": "",
    "Photo 1": "",
    "Photo 2": "",
    "Photo 3": "",
    "Photo 4": "",
    "Photo 5": "",
    "Etat": "",
    "ID Marque": "",
    "Nom Marque": "",
    "ID Catégorie principale parente": "",
    "Catégorie principale parente": "",
    "ID Sous-catégorie principale": "",
    "Sous-catégorie principale": "",
    "ID Catégorie secondaire 1 parente": "",
    "Catégorie secondaire 1 parente": "",
    "ID Sous-catégorie secondaire 1": "",
    "Sous-catégorie secondaire 1": "",
    "ID Catégorie secondaire 2 parente": "",
    "Catégorie secondaire 2 parente": "",
    "ID Sous-catégorie secondaire 2": "",
    "Sous-catégorie secondaire 2": "",
    "Prix du produit (TTC hors remise)": "",
    "Montant de la remise": "",
    "Pourcentage de remise": "",
    "Type de remise": "",
    "Date début remise": "",
    "Date fin remise": "",
    "Taux de tva": "",
    "Garantie": "",
    "Genre": "",
    "Matière": "",
    "Couleur": "",
    "Taille": "",
    "Quantité": "",
    "Pointure": "",
    "Dimension": "",
    "Age": "",
}


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def fetch_search_results(product_query, number_of_pages, associate_id,rainforest_api_key):
    params = {
        'api_key': rainforest_api_key,
        'type': 'search',
        'amazon_domain': 'amazon.fr',
        'search_term': product_query,
        'associate_id': associate_id,
        'max_page': int(number_of_pages)
    }
    api_result = httpx.get(
        'https://api.rainforestapi.com/request', params=params, timeout=120)
    data = api_result.json()
    return data


def fetch_product(asin, associate_id, amazon_domain,rainforest_api_key):
    params = {
        'api_key': rainforest_api_key,
        'type': 'product',
        'asin': asin,
        'associate_id': associate_id,
        'amazon_domain': amazon_domain
    }
    api_result = httpx.get(
        'https://api.rainforestapi.com/request', params=params, timeout=120)
    data_product = api_result.json()
    return data_product


async def main(product_queries, associate_id, number_of_pages, amazon_domain,rainforest_api_key):

    
    ts = int(time.time())
    for product_query in product_queries:
        print(f"### {product_query} ###")
        rows = []
        search_results = []
        data = fetch_search_results(product_query, number_of_pages, associate_id,rainforest_api_key)

        directory = f"exports/{ts}_{slugify(product_query)}"

        path = os.path.join(os.getcwd(), directory)
        os.mkdir(path)

        json_file_name = f"{path}/{ts}_search_{slugify(product_query)}.json"
        
        # print(f'json_file_name :{json_file_name}')
        
        with open(json_file_name, 'w') as f:
            json.dump(data,f)

        search_results.extend(data['search_results'])

        data = pd.DataFrame.from_dict(search_results)
        print(
            f"Found {len(search_results)} products for \"{product_query}\".")

        # for test limit to 5 products
        # search_results = search_results[:5]
        for ind, product in enumerate(tqdm(search_results, desc="Fetching products")):

            asin = product['asin']
            data_product = fetch_product(asin, associate_id, amazon_domain,rainforest_api_key)
            json_product_file_name = f"{path}/{ts}_{ind}_product_{slugify(product_query)}.json"
            # print(f'json_product_file_name :{json_product_file_name}')
            with open(json_product_file_name, 'w') as f:
                json.dump(data_product,f)

            product = data_product['product']
            attributes = []
            if 'attributes' in product:
                attributes = [
                    f"- {p['name']}:{p['value']}\n" for p in product['attributes']]
            images = []
            if 'images' in product:
                images = [p['link'] for p in product['images']] 
            
            categories =[]
            if 'categories' in product:
                categories = [[p['name'], p['category_id'] if 'category_id' in p else ""] for p in product['categories']]

            row = default_row.copy()
            row["ID produit"] = product['asin'] if 'asin' in product else ""
            row["Référence du produit (AmazonID)"] = product['asin'] if 'asin' in product else ""
            row["Référence"] = product['asin'] if 'asin' in product else "Amazon"
            row["Nom du produit"] = product['title'] if 'title' in product else ""
            row["Description courte"] = product['feature_bullets_flat'] if 'feature_bullets_flat' in product else ""
            row["Description longue"] = " ".join(product['feature_bullets'])[:254] if "feature_bullets" in product else ""
            row["Mots clés"] = product['keywords'] if 'keywords' in product else ""
            row["Caractéristiques"] = "".join(
                attributes) if len(attributes) > 0 else ""
            row["Poids"] = ""
            row["Nombre de produits en stock"] = ""
            row["Titre de la page"] = product['title'] if 'title' in product else ""
            row["URL (sans .html)"] = data_product['request_metadata']['amazon_url'] if 'request_metadata' in data_product else ""
            row["Méta description"] = product['feature_bullets_flat'][:159] if 'feature_bullets_flat' in product else ""
            row["Lien d'affiliation"] = f"{data_product['request_metadata']['amazon_url']}&tag={associate_id}" if 'request_metadata' in data_product else ""
            row["Photo 1"] = product['main_image']['link'] if 'main_image' in product else ""
            row["Photo 2"] = images[0] if len(images) > 0 else ""
            row["Photo 3"] = images[1] if len(images) > 1 else ""
            row["Photo 4"] = images[2] if len(images) > 2 else ""
            row["Photo 5"] = images[3] if len(images) > 3 else ""
            row["Etat"] = "Affiché"
            row["ID Marque"] = ""
            row["Nom Marque"] = product['brand'] if 'brand' in product else ""

            row["ID Catégorie principale parente"] = categories[0][1] if len(
                categories) > 0 else ""
            row["Catégorie principale parente"] = categories[0][0] if len(
                categories) > 0 else ""

            row["ID Sous-catégorie principale"] = categories[1][1] if len(
                categories) > 1 else ""
            row["Sous-catégorie principale"] = categories[1][0] if len(
                categories) > 1 else ""

            row["ID Catégorie secondaire 1 parente"] = categories[2][1] if len(
                categories) > 2 else ""
            row["Catégorie secondaire 1 parente"] = categories[2][0] if len(
                categories) > 2 else ""

            row["ID Sous-catégorie secondaire 1"] = categories[3][1] if len(
                categories) > 3 else ""
            row["Sous-catégorie secondaire 1"] = categories[3][0] if len(
                categories) > 3 else ""

            row["ID Catégorie secondaire 2 parente"] = categories[4][1] if len(
                categories) > 4 else ""
            row["Catégorie secondaire 2 parente"] = categories[4][0] if len(
                categories) > 4 else ""

            row["ID Sous-catégorie secondaire 2"] = categories[5][1] if len(
                categories) > 5 else ""
            row["Sous-catégorie secondaire 2"] = categories[5][0] if len(
                categories) > 5 else ""

            row["Prix du produit (TTC hors remise)"] = product['buybox_winner']['price']['value'] if 'price' in product[
                'buybox_winner'] and 'value' in product['buybox_winner']['price'] else 0
            row["Montant de la remise"] = ""
            row["Pourcentage de remise"] = ""
            row["Type de remise"] = ""
            row["Date début remise"] = ""
            row["Date fin remise"] = ""
            row["Taux de tva"] = ""
            row["Garantie"] = ""
            row["Genre"] = ""
            row["Matière"] = ""
            row["Couleur"] = ""
            row["Taille"] = ""
            row["Quantité"] = ""
            row["Pointure"] = ""
            row["Dimension"] = ""
            row["Age"] = ""
            rows.append(row)

        if len(rows) > 0:
            df = pd.DataFrame(rows, columns=default_row.keys())
            csv = convert_df(df)
            csv_file_name = f"{path}/{ts}_{slugify(product_query)}.csv"
            with open(csv_file_name, 'wb') as f:
                f.write(csv)
            print(f"Saved {len(rows)} products to {csv_file_name}.csv")


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('config_file', help='YAML config file')
    args = args.parse_args()

    # configparser = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    with open(args.config_file, "r") as file:
        config = yaml.safe_load(file)

    product_queries = config['product_queries']

    rainforest_api_key = config['rainforest_api_key']
    associate_id = config['associate_id']
    amazon_domain = config['amazon_domain']
    number_of_pages = config['number_of_pages']
    
    print(product_queries)
    asyncio.run(main(product_queries, associate_id,number_of_pages, amazon_domain,rainforest_api_key))
