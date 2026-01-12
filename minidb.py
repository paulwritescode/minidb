import json
import re
import os
from typing import List, Dict, Any


class MiniDB:
    def __init__(self, db_name: str = "default", persist_file: str = None):
        self.db_name = db_name
        self.tables = {}  # table_name: {'columns': [...], 'data': [], 'indexes': {}}
        self.persist_file = persist_file
        if persist_file:
            self.load()

    def execute(self, query: str) -> Any:
        query = query.strip()
        query_upper = query.upper()
        
        if query_upper.startswith("CREATE TABLE"):
            return self._create_table(query)
        elif query_upper.startswith("INSERT INTO"):
            return self._insert(query)
        elif query_upper.startswith("SELECT"):
            return self._select(query)
        elif query_upper.startswith("UPDATE"):
            return self._update(query)
        elif query_upper.startswith("DELETE FROM"):
            return self._delete(query)
        else:
            raise ValueError("Unsupported query")

    def _create_table(self, query: str):
        # Parse: CREATE TABLE table_name (col1 TYPE [PRIMARY|UNIQUE|INDEX], ...)
        # Remove extra whitespace and newlines
        query_clean = ' '.join(query.split())
        query_upper = query_clean.upper()
        
        match = re.match(r"CREATE TABLE (\w+) \((.+)\)", query_upper)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1).lower()  # Store table names in lowercase
        if table_name in self.tables:
            raise ValueError(f"Table {table_name} already exists")
        
        columns_str = match.group(2).split(',')
        columns = []
        
        for col in columns_str:
            parts = col.strip().split()
            if len(parts) < 2:
                raise ValueError("Invalid column definition")
            
            col_name = parts[0].lower()  # Store column names in lowercase
            col_type = parts[1]
            primary = 'PRIMARY' in parts
            unique = 'UNIQUE' in parts
            index = 'INDEX' in parts or primary  # Primary keys are automatically indexed
            
            if col_type not in ['INT', 'STRING', 'BOOLEAN']:
                raise ValueError(f"Unsupported type: {col_type}")
            
            columns.append({
                'name': col_name, 
                'type': col_type, 
                'primary': primary, 
                'unique': unique, 
                'index': index
            })
        
        self.tables[table_name] = {
            'columns': columns, 
            'data': [], 
            'indexes': {}
        }
        
        # Build indexes
        for col in columns:
            if col['index']:
                self.tables[table_name]['indexes'][col['name']] = {}
        
        self._save()
        return f"Table {table_name} created"

    def _insert(self, query: str):
        # Parse: INSERT INTO table_name (col1, col2) VALUES (val1, val2)
        match = re.match(r"INSERT INTO (\w+) \((.+)\) VALUES \((.+)\)", query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1).lower()  # Convert to lowercase
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found")
        
        cols = [c.strip().lower() for c in match.group(2).split(',')]
        vals_str = match.group(3).split(',')
        
        table = self.tables[table_name]
        col_map = {c['name']: c for c in table['columns']}  # Column names already lowercase
        
        # Validate columns exist
        for col in cols:
            if col not in col_map:
                raise ValueError(f"Column {col} not found")
        
        vals = []
        for i, val_str in enumerate(vals_str):
            col_name = cols[i]
            col = col_map[col_name]
            val = self._cast_value(val_str.strip(), col['type'])
            vals.append(val)
        
        row = dict(zip(cols, vals))
        
        # Enforce primary/unique constraints
        for col in table['columns']:
            if col['primary'] or col['unique']:
                key_col = col['name']
                if key_col in row:
                    existing = [r[key_col] for r in table['data'] if key_col in r]
                    if row[key_col] in existing:
                        raise ValueError(f"Duplicate value for {key_col}")
        
        table['data'].append(row)
        
        # Update indexes
        row_idx = len(table['data']) - 1
        for idx_col, idx_dict in table['indexes'].items():
            if idx_col in row:
                val = row[idx_col]
                if val not in idx_dict:
                    idx_dict[val] = []
                idx_dict[val].append(row_idx)
        
        self._save()
        return "Insert successful"

    def _select(self, query: str):
        # Parse: SELECT cols FROM table [JOIN table2 ON col1=col2] [WHERE condition]
        query_upper = query.upper()
        original_query = query  # Keep original for WHERE clause
        
        parts = query_upper.split(' FROM ')
        if len(parts) < 2:
            raise ValueError("Invalid SELECT syntax")
        
        select_part = parts[0][7:].strip()  # After SELECT
        from_part = parts[1]
        
        # Check for JOIN
        join_match = re.search(r"(\w+) JOIN (\w+) ON (\w+)=(\w+)", from_part)
        where_part = None
        
        if ' WHERE ' in from_part:
            from_part, _ = from_part.split(' WHERE ', 1)
            # Extract WHERE clause from original query to preserve case
            where_match = re.search(r' WHERE (.+)', original_query, re.IGNORECASE)
            if where_match:
                where_part = where_match.group(1)
        
        if join_match:
            table1 = join_match.group(1).lower()
            table2 = join_match.group(2).lower()
            join_col1 = join_match.group(3).lower()
            join_col2 = join_match.group(4).lower()
            tables = [table1, table2]
        else:
            tables = [from_part.strip().split()[0].lower()]
        
        # Validate tables exist
        for t in tables:
            if t not in self.tables:
                raise ValueError(f"Table {t} not found")
        
        cols = [c.strip() for c in select_part.split(',')] if select_part != '*' else None
        
        # Fetch data
        results = []
        if len(tables) == 1:
            table = self.tables[tables[0]]
            data = self._filter_data(table['data'], where_part, table['columns'], table['indexes'])
            results = self._project_cols(data, cols, tables[0])
        else:
            # Simple INNER JOIN
            t1 = self.tables[tables[0]]
            t2 = self.tables[tables[1]]
            
            # Use index if available for join column
            if join_col1 in t1['indexes']:
                idx = t1['indexes'][join_col1]
                for val, row_idxs in idx.items():
                    matching_t2 = [r for r in t2['data'] if r.get(join_col2) == val]
                    for row_idx in row_idxs:
                        row1 = t1['data'][row_idx]
                        for row2 in matching_t2:
                            joined_row = {f"{tables[0]}.{k}": v for k, v in row1.items()}
                            joined_row.update({f"{tables[1]}.{k}": v for k, v in row2.items()})
                            results.append(joined_row)
            else:
                # Fallback to nested loop
                for row1 in t1['data']:
                    for row2 in t2['data']:
                        if row1.get(join_col1) == row2.get(join_col2):
                            joined_row = {f"{tables[0]}.{k}": v for k, v in row1.items()}
                            joined_row.update({f"{tables[1]}.{k}": v for k, v in row2.items()})
                            results.append(joined_row)
            
            # Apply WHERE on joined results
            if where_part:
                results = [r for r in results if self._eval_condition(r, where_part)]
        
        return results

    def _update(self, query: str):
        # Parse: UPDATE table SET col=val [, col=val] WHERE condition
        match = re.match(r"UPDATE (\w+) SET (.+) WHERE (.+)", query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1).lower()
        set_part = match.group(2)
        where_part = match.group(3)
        
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found")
        
        table = self.tables[table_name]
        col_map = {c['name']: c for c in table['columns']}
        
        # Parse SET clause
        set_pairs = [p.strip().split('=', 1) for p in set_part.split(',')]
        updates = {}
        
        for pair in set_pairs:
            if len(pair) != 2:
                raise ValueError("Invalid SET clause")
            col_name = pair[0].strip()
            val_str = pair[1].strip()
            
            if col_name not in col_map:
                raise ValueError(f"Column {col_name} not found")
            
            col_type = col_map[col_name]['type']
            updates[col_name] = self._cast_value(val_str, col_type)
        
        # Filter rows to update
        data = table['data']
        filtered_idxs = [i for i, row in enumerate(data) if self._eval_condition(row, where_part)]
        
        for idx in filtered_idxs:
            old_row = data[idx]
            
            # Check constraints before updating
            for col, val in updates.items():
                col_info = col_map[col]
                if (col_info['primary'] or col_info['unique']) and val != old_row.get(col):
                    existing = [r[col] for r in data if col in r and r != old_row]
                    if val in existing:
                        raise ValueError(f"Duplicate value for {col}")
            
            # Update indexes (remove old values)
            for idx_col, idx_dict in table['indexes'].items():
                if idx_col in old_row:
                    old_val = old_row[idx_col]
                    if old_val in idx_dict and idx in idx_dict[old_val]:
                        idx_dict[old_val].remove(idx)
            
            # Apply updates
            for col, val in updates.items():
                old_row[col] = val
            
            # Update indexes (add new values)
            for idx_col, idx_dict in table['indexes'].items():
                if idx_col in old_row:
                    new_val = old_row[idx_col]
                    if new_val not in idx_dict:
                        idx_dict[new_val] = []
                    idx_dict[new_val].append(idx)
        
        self._save()
        return f"{len(filtered_idxs)} rows updated"

    def _delete(self, query: str):
        # Parse: DELETE FROM table WHERE condition
        match = re.match(r"DELETE FROM (\w+) WHERE (.+)", query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1).lower()
        where_part = match.group(2)
        
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found")
        
        table = self.tables[table_name]
        data = table['data']
        
        # Find rows to delete
        filtered_idxs = sorted([i for i, row in enumerate(data) if self._eval_condition(row, where_part)], reverse=True)
        
        for idx in filtered_idxs:
            row = data.pop(idx)
            
            # Update indexes
            for idx_col, idx_dict in table['indexes'].items():
                if idx_col in row:
                    val = row[idx_col]
                    if val in idx_dict and idx in idx_dict[val]:
                        idx_dict[val].remove(idx)
                    
                    # Shift subsequent indices
                    for other_val, other_idxs in idx_dict.items():
                        for i, other_idx in enumerate(other_idxs):
                            if other_idx > idx:
                                other_idxs[i] = other_idx - 1
        
        self._save()
        return f"{len(filtered_idxs)} rows deleted"

    def _filter_data(self, data: List[Dict], where_part: str, columns: List[Dict], indexes: Dict) -> List[Dict]:
        if not where_part:
            return data
        
        # Simple optimization: use index for single equality condition
        if '=' in where_part and 'AND' not in where_part.upper() and 'OR' not in where_part.upper():
            # Replace = with == for parsing
            condition = re.sub(r'(?<![=!<>])=(?!=)', '==', where_part)
            parts = condition.split('==')
            if len(parts) == 2:
                col = parts[0].strip()
                val_str = parts[1].strip()
                
                if col in indexes:
                    col_info = next((c for c in columns if c['name'] == col), None)
                    if col_info:
                        val = self._cast_value(val_str, col_info['type'])
                        idx_dict = indexes[col]
                        row_idxs = idx_dict.get(val, [])
                        return [data[i] for i in row_idxs if i < len(data)]
        
        # Fallback to full scan
        return [row for row in data if self._eval_condition(row, where_part)]

    def _eval_condition(self, row: Dict, where_part: str) -> bool:
        # Simple condition evaluation for =, AND, OR
        condition = where_part
        
        # Replace = with == for Python evaluation
        condition = re.sub(r'(?<![=!<>])=(?!=)', '==', condition)
        
        # Replace boolean literals
        condition = re.sub(r'\bfalse\b', 'False', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\btrue\b', 'True', condition, flags=re.IGNORECASE)
        
        # Replace column names with their values, being careful about word boundaries
        for col, val in row.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(col) + r'\b'
            if isinstance(val, str):
                replacement = f"'{val}'"
            elif isinstance(val, bool):
                replacement = str(val)
            else:
                replacement = str(val)
            condition = re.sub(pattern, replacement, condition, flags=re.IGNORECASE)
        
        # Replace SQL operators with Python operators
        condition = condition.replace('AND', 'and').replace('OR', 'or')
        
        try:
            return eval(condition)
        except Exception as e:
            raise ValueError(f"Invalid WHERE condition: {where_part} (evaluated as: {condition})")

    def _project_cols(self, data: List[Dict], cols: List[str], table_name: str) -> List[Dict]:
        if not cols or cols == ['*']:
            return data
        
        return [{c: row.get(c) for c in cols if c in row} for row in data]

    def _cast_value(self, val_str: str, typ: str):
        val_str = val_str.strip()
        
        if typ == 'INT':
            return int(val_str)
        elif typ == 'STRING':
            # Remove quotes if present
            if (val_str.startswith("'") and val_str.endswith("'")) or \
               (val_str.startswith('"') and val_str.endswith('"')):
                return val_str[1:-1]
            return val_str
        elif typ == 'BOOLEAN':
            return val_str.lower() in ['true', '1', 'yes']
        
        return val_str

    def _save(self):
        if self.persist_file:
            try:
                with open(self.persist_file, 'w') as f:
                    json.dump(self.tables, f, default=str, indent=2)
            except Exception as e:
                print(f"Warning: Could not save to {self.persist_file}: {e}")

    def load(self):
        if self.persist_file and os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, 'r') as f:
                    self.tables = json.load(f)
                
                # Rebuild indexes
                for table_name, table in self.tables.items():
                    if 'indexes' not in table:
                        table['indexes'] = {}
                    
                    # Clear and rebuild indexes
                    for col in table['columns']:
                        if col['index']:
                            table['indexes'][col['name']] = {}
                    
                    # Populate indexes
                    for i, row in enumerate(table['data']):
                        for idx_col, idx_dict in table['indexes'].items():
                            if idx_col in row:
                                val = row[idx_col]
                                if val not in idx_dict:
                                    idx_dict[val] = []
                                idx_dict[val].append(i)
            except Exception as e:
                print(f"Warning: Could not load from {self.persist_file}: {e}")

    def repl(self):
        print("=" * 60)
        print("🗄️  MiniDB Interactive REPL")
        print("=" * 60)
        print("Welcome to MiniDB! A simple relational database management system.")
        print("\nSupported commands:")
        print("  CREATE TABLE - Create a new table with columns")
        print("  INSERT INTO  - Insert data into a table")
        print("  SELECT       - Query data from tables")
        print("  UPDATE       - Update existing records")
        print("  DELETE FROM  - Delete records from tables")
        print("  .help        - Show this help message")
        print("  .tables      - List all tables")
        print("  .describe    - Show table structure")
        print("  .clear       - Clear the screen")
        print("  exit         - Exit the REPL")
        print("\nExample:")
        print("  CREATE TABLE users (id INT PRIMARY UNIQUE INDEX, name STRING, active BOOLEAN)")
        print("  INSERT INTO users (id, name, active) VALUES (1, 'Alice', true)")
        print("  SELECT * FROM users WHERE active=true")
        print("-" * 60)
        
        while True:
            try:
                query = input("\nminidb> ").strip()
                
                if not query:
                    continue
                    
                if query.lower() == 'exit':
                    print("Goodbye! 👋")
                    break
                elif query.lower() == '.help':
                    self._show_help()
                elif query.lower() == '.tables':
                    self._show_tables()
                elif query.lower().startswith('.describe'):
                    parts = query.split()
                    if len(parts) > 1:
                        self._describe_table(parts[1])
                    else:
                        print("Usage: .describe <table_name>")
                elif query.lower() == '.clear':
                    import os
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                else:
                    result = self.execute(query)
                    if isinstance(result, list):
                        if result:
                            self._print_table(result)
                        else:
                            print("No results returned.")
                    else:
                        print(f"✅ {result}")
                        
            except KeyboardInterrupt:
                print("\n\nUse 'exit' to quit or Ctrl+C again to force exit.")
                try:
                    input()
                except KeyboardInterrupt:
                    print("\nForce exit. Goodbye! 👋")
                    break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _show_help(self):
        print("\n📚 MiniDB Help")
        print("-" * 40)
        print("Data Types:")
        print("  INT     - Integer numbers")
        print("  STRING  - Text strings")
        print("  BOOLEAN - true/false values")
        print("\nConstraints:")
        print("  PRIMARY - Primary key (unique, indexed)")
        print("  UNIQUE  - Unique values only")
        print("  INDEX   - Create index for faster queries")
        print("\nSQL Examples:")
        print("  CREATE TABLE products (")
        print("    id INT PRIMARY UNIQUE INDEX,")
        print("    name STRING,")
        print("    price INT,")
        print("    available BOOLEAN")
        print("  )")
        print("  INSERT INTO products (id, name, price, available) VALUES (1, 'Laptop', 999, true)")
        print("  SELECT * FROM products WHERE price > 500")
        print("  UPDATE products SET price=899 WHERE id=1")
        print("  DELETE FROM products WHERE available=false")
        print("  SELECT * FROM orders JOIN products ON orders.product_id=products.id")

    def _show_tables(self):
        if not self.tables:
            print("No tables found. Create your first table!")
            return
            
        print(f"\n📋 Database Tables ({len(self.tables)} total)")
        print("-" * 50)
        for table_name, table_data in self.tables.items():
            row_count = len(table_data['data'])
            index_count = len(table_data['indexes'])
            print(f"  {table_name:<20} {row_count:>6} rows, {index_count:>2} indexes")

    def _describe_table(self, table_name):
        table_name = table_name.lower()
        if table_name not in self.tables:
            print(f"❌ Table '{table_name}' not found.")
            return
            
        table = self.tables[table_name]
        print(f"\n📊 Table: {table_name}")
        print("-" * 50)
        print(f"Rows: {len(table['data'])}")
        print(f"Columns: {len(table['columns'])}")
        print(f"Indexes: {len(table['indexes'])}")
        print("\nColumn Structure:")
        print("  Name          Type      Constraints")
        print("  " + "-" * 40)
        
        for col in table['columns']:
            constraints = []
            if col['primary']:
                constraints.append('PRIMARY')
            if col['unique']:
                constraints.append('UNIQUE')
            if col['index']:
                constraints.append('INDEX')
            
            constraint_str = ', '.join(constraints) if constraints else '-'
            print(f"  {col['name']:<12} {col['type']:<8} {constraint_str}")

    def _print_table(self, data):
        if not data:
            return
            
        # Get all unique keys from all rows
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())
        all_keys = sorted(list(all_keys))
        
        # Calculate column widths
        col_widths = {}
        for key in all_keys:
            col_widths[key] = max(len(str(key)), 
                                max(len(str(row.get(key, ''))) for row in data))
        
        # Print header
        print("\n" + "+" + "+".join("-" * (col_widths[key] + 2) for key in all_keys) + "+")
        header = "|" + "|".join(f" {key:<{col_widths[key]}} " for key in all_keys) + "|"
        print(header)
        print("+" + "+".join("-" * (col_widths[key] + 2) for key in all_keys) + "+")
        
        # Print rows
        for row in data:
            row_str = "|" + "|".join(f" {str(row.get(key, '')):<{col_widths[key]}} " for key in all_keys) + "|"
            print(row_str)
        
        print("+" + "+".join("-" * (col_widths[key] + 2) for key in all_keys) + "+")
        print(f"({len(data)} row{'s' if len(data) != 1 else ''})")


if __name__ == "__main__":
    # Test the REPL
    db = MiniDB(persist_file='test_db.json')
    db.repl()