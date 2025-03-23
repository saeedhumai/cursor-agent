from typing import List
from pydantic import BaseModel

# Define the Todo model
class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# In-memory storage for todos
class TodoStore:
    def __init__(self):
        self.todos: List[Todo] = []

    def add_todo(self, todo: Todo):
        self.todos.append(todo)

    def get_all_todos(self) -> List[Todo]:
        return self.todos

    def get_todo_by_id(self, todo_id: int) -> Todo:
        return next((todo for todo in self.todos if todo.id == todo_id), None)

    def update_todo(self, todo_id: int, updated_todo: Todo):
        todo = self.get_todo_by_id(todo_id)
        if todo:
            todo.title = updated_todo.title
            todo.description = updated_todo.description
            todo.completed = updated_todo.completed

    def delete_todo(self, todo_id: int):
        self.todos = [todo for todo in self.todos if todo.id != todo_id]