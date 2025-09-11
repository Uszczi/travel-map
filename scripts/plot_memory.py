import matplotlib.pyplot as plt

x = list(range(1, 11))
x = [i / 10 for i in x]
y1 = [291492.00] * 10  # Seria 1
y2 = [293668.00] * 10  # Seria 2
y3 = [294308.00] * 10  # Seria 3
#  -------------------------------

plt.figure()
plt.ylim(200000, 400000)
plt.plot(x, y1, label="Losowy algorytm")
plt.plot(x, y2, label="A*")
plt.plot(x, y3, label="Depth First Search")

plt.xlabel("Czas w milisekundach")
plt.ylabel("Zajmowana ilość pamięci w KB")
plt.title("Zajmowanej ilość pamięci")
plt.legend()
plt.grid(True)

plt.tight_layout()
# Jeśli chcesz zapisać do pliku, odkomentuj poniższą linię:
# plt.savefig("wykres_trzy_serie.png", dpi=150, bbox_inches="tight")
plt.show()
