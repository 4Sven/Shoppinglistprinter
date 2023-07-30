#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto3
from grocery import Grocery
from category import Category
from recipe import Recipe

def loadFromDB(category_value, dynamodb, table_name):
    table = dynamodb.Table(table_name)

    response = table.scan(
        FilterExpression='category = :val',
        ExpressionAttributeValues={':val': category_value}
    )

    items = response.get('Items', [])
    return items

def main():
    # Your main program logic goes here
    print("Connection Database…")

    # Create a Session with the default profile
    session = boto3.session.Session()

    dynamodb = session.resource('dynamodb')

    table_name='Shoppinglist'
    grocery_list = []

    # Daten für Einkaufsliste aus der Datenbank auslesen
    items = loadFromDB('grocery', dynamodb, table_name)
    for item in items:
        #print(f"{item['name']} -> {item['quantity']}")
        #Array befüllen
        grocery_list.append(Grocery(item['itemCategory'], item['name'], item['quantity']))

    #print(f"{len(grocery_list)} Elemente geladen")

    # Read Categories from DB and order this
    unordered_category_list = []

    categories_from_db = loadFromDB('category', dynamodb, table_name)
    for category in categories_from_db:
        unordered_category_list.append(Category(category['name'], category['order']))

    sorted_categories = sorted(unordered_category_list, key=lambda x: x.order)

    #for category in sorted_categories:
    #    print(f"{category.name}")

    # Read Recipes from DB
    unordered_recipe_list = []
    recipes_from_db = loadFromDB('recipe', dynamodb, table_name)
    for recipe in recipes_from_db:
        #print(recipe)
        unordered_recipe_list.append(Recipe(recipe['name']))

    sorted_recipes = sorted(unordered_recipe_list, key=lambda x: x.name)

    groceries_by_category = {}

    # Build a Dictonary for groceries
    for grocery in grocery_list:
        category = grocery.category
        if category in groceries_by_category:
            # Append the grocery to the existing category list
            groceries_by_category[category].append(grocery)
        else:
            # Create a new list for the category and add the grocery to it
            groceries_by_category[category] = [grocery]

    # Ready for printing
    print("Gerichte")
    for meal in sorted_recipes:
        print(f"  {meal.name}")
    for category in sorted_categories:
        grocery_in_category = groceries_by_category.get(category.name, [])
        if len(grocery_in_category) > 0:
            print(f"Category: {category.name}")
            for grocery in grocery_in_category:
                print(f"  {grocery.name} -> {grocery.quantity}")
            print("---")

if __name__ == "__main__":
    main()

