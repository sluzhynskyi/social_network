# Social Network REST-api
Project for StarNavi company, where used Postgresql and Flask
## Task
The task is to develop a REST-api and interface for implementation of the models for this **Social network Api** system:
* models:
    * **user** and **post**
* object:
    * **likes** 
* possible actions:
    * Check analytics about how many likes was made. Example url ```/analitics/?date_from=2020-02-02&date_to=2020-02-15```
    * View user activity (last login date, last request date)
    
## ER diagram
![Untitled Diagram (1)](https://user-images.githubusercontent.com/44615981/85178249-b2011a80-b286-11ea-842c-50a0bd8caea7.png?style=centerme) </br>

## Endpoints
* ```Post    /users``` Register user, json body ```{"username" : "admin", "password" : "admin"}```
* ```Get    /users```  Gets all users: username and public_id
* ```Get    /users/<str:username>```  Gets specific user: username and public_id
* ```Get    /users/<str:username>/activity```  Gets specific user: last login date and last request date
* ```Post    /session```  authenticates credentials, and returns JWT token
* ```Delete    /session```  Log out
* ```Post    /posts``` Creates post: Title, body of post
* ```Get    /posts``` Gets all posts: Title, body of post, published date, publisher
* ```Get    /posts/<int:post_id>``` Gets specific posts: Title, body of post, published date, publisher
* ```Post    /posts/<int:post>/likes``` Like post or Unlike (toggle)
* ```Get    /posts/<int:post>/likes``` Get all likes that made by users for specific post
* ```Get    /analitics/?date_from=<date>&date_to=<date>``` Check analytics about how many likes was made. Example url


