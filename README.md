# MiniDB - Interactive SQL Database Management System

A complete relational database management system (RDBMS) built from scratch in Python, featuring a modern web interface with shadcn/ui inspired design.

## 🎯 Project Overview

This project implements a fully functional RDBMS that supports:
- **SQL Interface**: Standard SQL commands (CREATE, INSERT, SELECT, UPDATE, DELETE)
- **Data Types**: INT, STRING, BOOLEAN with proper type validation
- **Constraints**: Primary keys, unique keys with enforcement
- **Indexing**: Hash-based indexes for query optimization
- **Joins**: INNER JOIN support with index optimization
- **Web Interface**: Modern web app with real-time SQL execution
- **Persistence**: JSON-based storage with automatic save/load

## 🚀 Quick Start

### **Option 1: Using Makefile (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd minidb_todo_app

# One-time setup (creates venv + installs dependencies)
make setup

# Start the web application
make start
```
Opens automatically at http://127.0.0.1:8001/

### **Option 2: Manual Setup**
```bash
# Navigate to project directory
cd minidb_todo_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
python3 app.py
```

### **Available Make Commands**
```bash
make setup    # Create virtual environment and install dependencies
make start    # Start the web application
make repl     # Start interactive REPL mode
make install  # Update dependencies (if venv exists)
make clean    # Remove venv and generated files
make help     # Show all available commands
```

### **Alternative Startup Methods**
```bash
make repl           # Interactive command-line SQL interface
python3 start_app.py  # Alternative startup script (manual setup required)
```

## 🎨 Modern Web Interface

### Design System
- **Style**: Lyra-inspired design with shadcn/ui principles
- **Colors**: Zinc base palette with orange accent theme
- **Typography**: JetBrains Mono for consistent code display
- **Components**: Modern cards, buttons, and form elements
- **Responsive**: Mobile-friendly grid layout

### Features
- **Live SQL Editor**: Syntax-highlighted input with focus states
- **Real-time Results**: Formatted table output with hover effects
- **Database Explorer**: Interactive table browser with metadata
- **Example Queries**: One-click query templates
- **Error Handling**: Clear error messages with visual feedback

## 📊 SQL Interface Examples

### Creating Tables
```sql
CREATE TABLE users (
    id INT PRIMARY UNIQUE INDEX,
    name STRING,
    email STRING UNIQUE,
    active BOOLEAN
)
```

### Inserting Data
```sql
INSERT INTO users (id, name, email, active) VALUES (1, 'Alice Johnson', 'alice@example.com', true)
INSERT INTO users (id, name, email, active) VALUES (2, 'Bob Smith', 'bob@example.com', false)
```

### Querying Data
```sql
SELECT * FROM users
SELECT * FROM users WHERE active=true
SELECT name, email FROM users WHERE active=true
```

### Updating Records
```sql
UPDATE users SET active=true WHERE id=2
UPDATE users SET name='Alice Cooper' WHERE email='alice@example.com'
```

### Joining Tables
```sql
CREATE TABLE orders (id INT PRIMARY UNIQUE INDEX, user_id INT INDEX, product STRING, amount INT)
INSERT INTO orders (id, user_id, product, amount) VALUES (1, 1, 'Laptop', 999)
SELECT * FROM users JOIN orders ON users.id=orders.user_id
```

### Deleting Records
```sql
DELETE FROM users WHERE active=false
DELETE FROM orders WHERE amount < 50
```

## 🏗️ Architecture

### Core Components

1. **Query Parser**: Regex-based SQL command parsing
2. **Storage Engine**: In-memory data structures with JSON persistence
3. **Index Manager**: Hash-based indexing for performance optimization
4. **Constraint Engine**: Primary key and unique constraint enforcement
5. **Join Engine**: Nested loop and index-optimized join algorithms

### Web Application Stack

- **Backend**: FastAPI for REST API endpoints
- **Frontend**: HTML with HTMX for dynamic interactions
- **Templating**: Jinja2 for server-side rendering
- **Styling**: Modern CSS with shadcn/ui design system
- **Typography**: JetBrains Mono font family

## 🧪 Interactive REPL Commands

The REPL supports both SQL commands and helper functions:

### SQL Commands
- `CREATE TABLE` - Create new tables
- `INSERT INTO` - Add data
- `SELECT` - Query data
- `UPDATE` - Modify records
- `DELETE FROM` - Remove records

### Helper Commands
- `.help` - Show help information
- `.tables` - List all tables
- `.describe <table>` - Show table structure
- `.clear` - Clear screen
- `exit` - Exit REPL

## 📁 Project Structure

```
minidb_todo_app/
├── .gitignore               # Git ignore rules
├── Makefile                # Build automation and project commands
├── minidb.py               # Core RDBMS implementation (600+ lines)
├── app.py                  # FastAPI web application
├── start_app.py            # Alternative startup script
├── templates/
│   ├── index.html         # Main SQL interface with modern design
│   ├── sql_result.html    # Query result formatting
│   └── tables_list.html   # Database table browser
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
└── SUMMARY.md             # Project summary
```

## 💡 **Getting Started Tips**

### **First Time Users**
1. Clone the repository
2. Run `make setup` (creates everything you need)
3. Run `make start` (launches the web app)
4. Visit http://127.0.0.1:8001/ in your browser

### **Daily Development**
- `make start` - Quick launch of web application
- `make repl` - Command-line SQL interface for testing
- `make clean` - Reset environment if needed

### **Example Workflow**
```bash
# First time
git clone <repo-url>
cd minidb_todo_app
make setup

# Every time you want to use it
make start

# For command-line SQL work
make repl
```

## 🔧 Technical Implementation

### Performance Optimizations
- **Hash Indexes**: O(1) lookup for indexed columns
- **Query Optimization**: Index-based filtering when possible
- **Efficient Joins**: Index-optimized joins with fallback to nested loops

### Data Integrity
- **Type Validation**: Automatic type casting and validation
- **Constraint Enforcement**: Primary key and unique key checking
- **Transaction Safety**: Atomic operations with rollback on errors

### Modern Design System
- **shadcn/ui Inspired**: Lyra style with zinc and orange theme
- **Typography**: JetBrains Mono for consistent code display
- **Responsive Layout**: CSS Grid with mobile-first approach
- **Interactive Elements**: Smooth transitions and hover effects

## 🎯 Key Features Demonstrated

### Database Engineering
- ✅ SQL query parsing and execution
- ✅ Hash-based indexing for performance
- ✅ Relational operations (joins, constraints)
- ✅ ACID-like properties with error handling
- ✅ Persistent storage with data integrity

### Web Development
- ✅ Modern REST API with FastAPI
- ✅ Dynamic frontend with HTMX
- ✅ Responsive design with modern CSS
- ✅ Real-time data updates
- ✅ Error handling and user feedback

### Software Architecture
- ✅ Clean separation of concerns
- ✅ Modular, extensible design
- ✅ Production-ready error handling
- ✅ Modern UI/UX principles

## 🚧 Current Limitations & Future Enhancements

### Current Limitations
- **Transactions**: No multi-statement transaction support
- **Complex Queries**: Limited WHERE clause operators (no >, <, LIKE)
- **Concurrency**: Single-user, no concurrent access
- **Storage**: In-memory with JSON persistence (not optimized for large datasets)

### Potential Enhancements
- **Query Optimizer**: Cost-based query planning
- **Storage Engine**: B-tree indexes, page-based storage
- **SQL Parser**: Full SQL grammar with ANTLR
- **Network Protocol**: Client-server architecture
- **Replication**: Master-slave setup for scalability

## 🏆 Project Achievements

This project successfully demonstrates:

1. **Database Fundamentals**: Complete RDBMS implementation from scratch
2. **SQL Proficiency**: Full SQL interface with proper parsing and execution
3. **Modern Web Development**: Contemporary web application with dynamic interactions
4. **Design Systems**: Implementation of modern UI/UX principles
5. **Software Engineering**: Clean architecture and production-ready code

## 📜 Credits & Attribution

- **Core Implementation**: Built from scratch using database theory principles
- **Web Framework**: FastAPI (https://fastapi.tiangolo.com/)
- **Frontend Enhancement**: HTMX (https://htmx.org/)
- **Design System**: Inspired by shadcn/ui (https://ui.shadcn.com/)
- **Typography**: JetBrains Mono (https://www.jetbrains.com/mono/)

## 📄 License

This project is for educational and demonstration purposes. Feel free to use, modify, and learn from the code.