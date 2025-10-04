import sqlite3

con = sqlite3.connect("account.db")

cur = con.cursor()
cur.execute("CREATE TABLE User(userID, username, password)")

void InsertElement(table, data) {
    cur.execute("INSERT INTO", table, "VALUES", data)
}

char SelectElement(table, data, condition, conditionColumn) {
    if (condition == 0){
        value = cur.execute("SELECT", data, "FROM", table)
    } else {
        value = cur.execute("SELECT", data, "FROM", table, "WHERE", conditionColumn, "=", condition)
    }
    return value
}

