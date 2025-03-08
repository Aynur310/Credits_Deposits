import tkinter as tk
from tkinter import messagebox
import sqlite3

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        amount REAL,
        percent REAL,
        term INTEGER,
        result TEXT
    )
''')
conn.commit()


class Credit:
    def __init__(self, amount, percent, term, type_of_credit):
        self.amount = amount
        self.percent = percent / 100 / 12
        self.term = term
        self.type_of_credit = type_of_credit

    def annuity_credit(self):
        if self.percent == 0:
            return self.amount / self.term
        annuity_formul = (self.percent * (1 + self.percent) ** self.term) / ((1 + self.percent) ** self.term - 1)
        return self.amount * annuity_formul

    def differentiated_credit(self):
        all_payments = []
        ordinary_sum = self.amount / self.term
        for i in range(self.term):
            percent_of_the_month = (self.amount - ordinary_sum * i) * self.percent
            all_payments.append(ordinary_sum + percent_of_the_month)
        return all_payments

    def calculate(self):
        if self.type_of_credit == "annuity":
            total = self.annuity_credit() * self.term
            result = f"Ежемесячный платеж: {round(self.annuity_credit(), 2)}\nОбщая выплата: {round(total, 2)}\nПереплата: {round(total - self.amount, 2)}"
        elif self.type_of_credit == "differentiated":
            total = sum(self.differentiated_credit())
            payments = "\n".join([f"Месяц {i + 1}: {round(p, 2)}" for i, p in enumerate(self.differentiated_credit())])
            result = f"Платежи по месяцам:\n{payments}\nОбщая выплата: {round(total, 2)}\nПереплата: {round(total - self.amount, 2)}"
        else:
            result = "Неверный тип кредита"

        cursor.execute("INSERT INTO calculations (amount, percent, term, type, result) VALUES (?, ?, ?, ?, ?)",
                       (self.amount, self.percent * 12 * 100, self.term, "Кредит", result))
        conn.commit()

        return result


class Deposit:
    def __init__(self, amount, percent, term, capitalization=True):
        self.amount = amount
        self.percent = percent / 100 / 12
        self.term = term
        self.capitalization = capitalization

    def calculate(self):
        if self.capitalization:
            final_pay = self.amount * (1 + self.percent) ** self.term
        else:
            final_pay = self.amount + self.amount * self.percent * self.term
        result = f"Итоговая сумма: {round(final_pay, 2)}\nНачисленные проценты: {round(final_pay - self.amount, 2)}"

        cursor.execute("INSERT INTO calculations (type, amount, percent, term, result) VALUES (?, ?, ?, ?, ?)",
                       ("Депозит", self.amount, self.percent * 12 * 100, self.term, result))
        conn.commit()

        return result


def calculate_credit():
    try:
        amount = float(entry_amount.get())
        percent = float(entry_percent.get())
        term = int(entry_term.get())
        type_of_credit = credit_type_var.get()
        credit = Credit(amount, percent, term, type_of_credit)
        result_label.config(text=credit.calculate())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числовые значения")


def calculate_deposit():
    try:
        amount = float(entry_amount.get())
        percent = float(entry_percent.get())
        term = int(entry_term.get())
        capitalization = capitalization_var.get()
        deposit = Deposit(amount, percent, term, capitalization)
        result_label.config(text=deposit.calculate())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные числовые значения")


root = tk.Tk()
root.title("Калькулятор Кредитов и Депозитов")
root.geometry("400x400")

tk.Label(root, text="Сумма").pack()
entry_amount = tk.Entry(root)
entry_amount.pack()

tk.Label(root, text="Процентная ставка (%)").pack()
entry_percent = tk.Entry(root)
entry_percent.pack()

tk.Label(root, text="Срок (месяцы)").pack()
entry_term = tk.Entry(root)
entry_term.pack()

credit_type_var = tk.StringVar(value="annuity")
tk.Label(root, text="Тип кредита").pack()
tk.Radiobutton(root, text="Аннуитетный", variable=credit_type_var, value="annuity").pack()
tk.Radiobutton(root, text="Дифференцированный", variable=credit_type_var, value="differentiated").pack()

btn_credit = tk.Button(root, text="Рассчитать кредит", command=calculate_credit)
btn_credit.pack()

capitalization_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Капитализация процентов (для депозита)", variable=capitalization_var).pack()
btn_deposit = tk.Button(root, text="Рассчитать депозит", command=calculate_deposit)
btn_deposit.pack()

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()

conn.close()
