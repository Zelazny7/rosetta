if add1naprop == 1 or avmvalue > 200000:
    iv_add1naprop = -1
elif add1naprop == 2:
    iv_add1naprop = 0
elif ((add1naprop == 4) and (avmvalue not in [-1, 25])) or (add1naprop > 4):
    iv_add1naprop = min(300_000, avmvalue)
else:
    iv_add1naprop = np.nan
