import requests
import matplotlib.pyplot as plt

# Fetch data from the FastAPI
response = requests.get("http://127.0.0.1:8000/tax-breakdown")
data = response.json()

# Separate keys and values
labels = list(data.keys())
values = list(data.values())

# Plot Pie Chart
plt.figure(figsize=(6, 6))
plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title("Where Did My Tax Go? - Pie Chart")
plt.axis('equal')
plt.tight_layout()
plt.show()

# Plot Bar Chart
plt.figure(figsize=(8, 6))
plt.bar(labels, values, color='skyblue')
plt.title("Where Did My Tax Go? - Bar Chart")
plt.ylabel("Amount")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
