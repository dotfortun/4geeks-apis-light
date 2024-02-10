<h1>Todo API</h1>

[TOC]

## Todo API Basics
This API is used for storing `Todo` objects that are owned by a `User`.

### Endpoints
[Interactive docs for all of these endpoints are available here.](/todo/docs)

#### `GET /users`
This endpoint gives you a list of `User` objects that are currently stored in the database.
The response body will look something like this:
```json
{
  "users": [
    {
      "name": "some_user",
      "id": 1
    },
    {
      "name": "some_other_user",
      "id": 2
    }
  ]
}
```

#### `POST /users/{username}`
This endpoint creates a new `User` and then returns a `User` object.
So if you make a `POST` request to `/users/some_new_user`, the response body will look something like this:
```json
{
  "name": "some_new_user",
  "id": 3
}
```

#### `GET /users/{username}`
This endpoint gives you a `User` and a list of their `Todo` objects.
So if you make a `GET` request to `/users/some_new_user`, the response body will look something like this:
```json
{
  "name": "some_new_user",
  "todos": [
    {
      "label": "Make a new todo item.",
      "is_done": true,
      "id": 1
    }
  ]
}
```

#### `DELETE /users/{username}`
This endpoint will `DELETE` a specific `User` object, and all of their `Todo` objects.
This endpoint will return an empty response with the status code `204` if it is successful.

#### `POST /todos/{username}`
This endpoint creates a new `Todo` and then returns that `Todo` object.
So if you make a `POST` request to `/todos/some_new_user` with the following JSON payload:
```json
{
  "label": "Make another new todo item!",
  "is_done": false
}
```

The response body will look something like this:
```json
{
  "label": "Make another new todo item!",
  "is_done": false,
  "id": 2
}
```

#### `PUT /todos/{todo_id}`
This endpoint allows you to edit a specific `Todo` object.
So if you make a `PUT` request to `/todos/2` with the following JSON payload:
```json
{
  "label": "Make another new todo item!",
  "is_done": true
}
```

The response body will look something like this:
```json
{
  "label": "Make another new todo item!",
  "is_done": true,
  "id": 2
}
```

#### `DELETE /todo/{todo_id}`
This endpoint will `DELETE` a specific `Todo` object.
This endpoint will return an empty response with the status code `204` if it is successful.

## FAQ

### I put my work down last night, why is my app breaking the next day?
This API is hosted on a virtual machine, and stores it's database in a file-based database called SQLite.  When it stops recieving traffic for a while, the virtual machine is recycled and the data on it is deleted.
