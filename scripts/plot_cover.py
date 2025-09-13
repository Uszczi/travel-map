import matplotlib.pyplot as plt

x = list(range(1, 16))

y1 = [4, 7, 8, 10, 13, 17, 17, 19, 19, 20, 20, 21, 23, 23, 23]
y2 = [3, 7, 9, 9, 11, 12, 13, 13, 13, 13, 14, 14, 14, 14, 14]
# y1 = [3, 6, 9, 13, 13, 14, 16, 17, 17, 18]
# y2 = [3, 6, 7, 8, 10, 11, 13, 13, 14, 14]
#  -------------------------------

plt.figure()
# plt.ylim(200000, 400000)
plt.plot(x, y1, label="Depth First Search")
plt.plot(x, y2, label="Losowy algorytm")

plt.xlabel("Numer drogi")
plt.ylabel("Procent pokrytych dróg")
plt.title("Pokrycie miasta względem wygenerowanej drogi")
plt.legend()
plt.grid(True)

plt.tight_layout()
# Jeśli chcesz zapisać do pliku, odkomentuj poniższą linię:
# plt.savefig("wykres_trzy_serie.png", dpi=150, bbox_inches="tight")
plt.show()
