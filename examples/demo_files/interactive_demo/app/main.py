from fastapi import FastAPI, HTTPException

app = FastAPI()

todos = []

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo):
    todos.append(todo)
    return todo

@app.get("/todos/", response_model=list[Todo])
def read_todos():
    return todos

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: Todo):
    for index, t in enumerate(todos):
        if t.id == todo_id:
            todos[index] = todo
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, t in enumerate(todos):
        if t.id == todo_id:
            del todos[index]
            return {"message": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")
