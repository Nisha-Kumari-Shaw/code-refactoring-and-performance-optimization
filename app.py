import webbrowser
import threading
from flask import Flask, jsonify, request, abort, render_template_string

app = Flask(__name__)

books = [
    {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
]

def find_book(book_id):
    return next((book for book in books if book["id"] == book_id), None)

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = find_book(book_id)
    if not book:
        abort(404, description="Book not found")
    return jsonify(book)

@app.route('/books', methods=['POST'])
def create_book():
    if not request.json or not all(k in request.json for k in ("title", "author", "year")):
        abort(400, description="Missing required fields")
    new_id = max((book["id"] for book in books), default=0) + 1
    new_book = {
        "id": new_id,
        "title": request.json["title"],
        "author": request.json["author"],
        "year": request.json["year"]
    }
    books.append(new_book)
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = find_book(book_id)
    if not book:
        abort(404, description="Book not found")
    if not request.json:
        abort(400, description="Request must be JSON")
    book["title"] = request.json.get("title", book["title"])
    book["author"] = request.json.get("author", book["author"])
    book["year"] = request.json.get("year", book["year"])
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = find_book(book_id)
    if not book:
        abort(404, description="Book not found")
    books = [b for b in books if b["id"] != book_id]
    return jsonify({"result": True})

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Library Inventory</title>
<style>
  /* Reset & base */
  * {
    box-sizing: border-box;
  }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f9fafd;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    color: #333;
  }
  header {
    background: #0052cc;
    color: white;
    padding: 1rem 2rem;
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
    box-shadow: 0 4px 10px rgb(0 0 0 / 0.1);
  }
  main {
    flex-grow: 1;
    max-width: 900px;
    margin: 2rem auto;
    padding: 1rem 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgb(0 0 0 / 0.1);
  }
  h2 {
    margin-top: 2rem;
    font-weight: 600;
    color: #0052cc;
  }
  ul#bookList {
    list-style: none;
    padding-left: 0;
    margin-top: 1rem;
  }
  ul#bookList li {
    background: #f1f5ff;
    border-radius: 8px;
    padding: 15px 20px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.1rem;
    box-shadow: 0 2px 6px rgb(0 0 0 / 0.05);
    transition: background-color 0.2s ease;
  }
  ul#bookList li:hover {
    background: #d6e0ff;
  }
  ul#bookList li span {
    flex: 1;
    padding-right: 10px;
  }
  button {
    background: #0052cc;
    border: none;
    color: white;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    margin-left: 8px;
    transition: background-color 0.2s ease;
  }
  button:hover {
    background: #003d99;
  }
  form {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem 1.5rem;
    margin-top: 1rem;
    align-items: center;
  }
  form input[type="text"],
  form input[type="number"] {
    flex-grow: 1;
    padding: 10px 12px;
    border: 2px solid #cbd5e1;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s ease;
  }
  form input[type="text"]:focus,
  form input[type="number"]:focus {
    outline: none;
    border-color: #0052cc;
    background: #f0f5ff;
  }
  form button[type="submit"] {
    flex-shrink: 0;
    min-width: 120px;
  }
  #editForm {
    background: #f9fafb;
    padding: 1rem 1.5rem;
    margin-top: 2rem;
    border-radius: 10px;
    box-shadow: inset 0 0 15px rgb(0 0 0 / 0.03);
    display: none;
  }
  #editForm h2 {
    margin-top: 0;
  }
  #cancelEdit {
    background: #d9534f;
  }
  #cancelEdit:hover {
    background: #b23125;
  }
  footer {
    text-align: center;
    padding: 1rem 0;
    font-size: 0.9rem;
    color: #555;
    background: #e3e8ef;
  }
  @media (max-width: 600px) {
    form {
      flex-direction: column;
    }
    form button[type="submit"] {
      width: 100%;
      min-width: unset;
    }
  }
</style>
</head>
<body>
  <header>Library Inventory</header>
  <main>
    <ul id="bookList"></ul>

    <h2>Add New Book</h2>
    <form id="bookForm" autocomplete="off">
      <input type="text" id="title" placeholder="Title" required />
      <input type="text" id="author" placeholder="Author" required />
      <input type="number" id="year" placeholder="Year" required min="0" />
      <button type="submit">Add Book</button>
    </form>

    <div id="editForm">
      <h2>Edit Book</h2>
      <form id="updateForm" autocomplete="off">
        <input type="hidden" id="editId" />
        <input type="text" id="editTitle" placeholder="Title" required />
        <input type="text" id="editAuthor" placeholder="Author" required />
        <input type="number" id="editYear" placeholder="Year" required min="0" />
        <button type="submit">Update Book</button>
        <button type="button" id="cancelEdit">Cancel</button>
      </form>
    </div>
  </main>
  <footer>© 2025 CODTECH Internship</footer>

<script>
  async function fetchBooks() {
    try {
      const res = await fetch('/books');
      if (!res.ok) throw new Error('Failed to fetch books');
      const books = await res.json();
      const list = document.getElementById('bookList');
      list.innerHTML = '';
      books.forEach(book => {
        const li = document.createElement('li');

        const textSpan = document.createElement('span');
        textSpan.textContent = `${book.title} by ${book.author} (${book.year}) [ID: ${book.id}]`;
        li.appendChild(textSpan);

        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.onclick = () => showEditForm(book);
        li.appendChild(editBtn);

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.onclick = () => deleteBook(book.id);
        li.appendChild(deleteBtn);

        list.appendChild(li);
      });
    } catch (e) {
      alert(e.message);
    }
  }

  document.getElementById('bookForm').addEventListener('submit', async e => {
    e.preventDefault();
    const title = document.getElementById('title').value.trim();
    const author = document.getElementById('author').value.trim();
    const year = parseInt(document.getElementById('year').value);
    if (!title || !author || !year) {
      alert('Please fill all fields correctly');
      return;
    }
    try {
      const res = await fetch('/books', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({title, author, year})
      });
      if (!res.ok) throw new Error('Failed to add book');
      document.getElementById('bookForm').reset();
      fetchBooks();
    } catch (e) {
      alert(e.message);
    }
  });

  function showEditForm(book) {
    document.getElementById('editForm').style.display = 'block';
    document.getElementById('editId').value = book.id;
    document.getElementById('editTitle').value = book.title;
    document.getElementById('editAuthor').value = book.author;
    document.getElementById('editYear').value = book.year;
    window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
  }

  document.getElementById('cancelEdit').addEventListener('click', () => {
    document.getElementById('editForm').style.display = 'none';
  });

  document.getElementById('updateForm').addEventListener('submit', async e => {
    e.preventDefault();
    const id = parseInt(document.getElementById('editId').value);
    const title = document.getElementById('editTitle').value.trim();
    const author = document.getElementById('editAuthor').value.trim();
    const year = parseInt(document.getElementById('editYear').value);
    if (!title || !author || !year) {
      alert('Please fill all fields correctly');
      return;
    }
    try {
      const res = await fetch(`/books/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({title, author, year})
      });
      if (!res.ok) throw new Error('Failed to update book');
      document.getElementById('editForm').style.display = 'none';
      fetchBooks();
    } catch (e) {
      alert(e.message);
    }
  });

  async function deleteBook(id) {
    if (!confirm('Are you sure you want to delete this book?')) return;
    try {
      const res = await fetch(`/books/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete book');
      fetchBooks();
    } catch (e) {
      alert(e.message);
    }
  }

  // Initial load
  fetchBooks();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()  # open browser after 1 second
    app.run(debug=True)
