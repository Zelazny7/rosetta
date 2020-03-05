

if add1naprop == 1 or avmvalue > 200000:
    iv_add1naprop = -1
elif add1naprop == 2:
    iv_add1naprop = 0
elif ((add1naprop == 4) and (avmvalue == 300_000)) or (add1naprop > 4):
    iv_add1naprop = 1
else:
    iv_add1naprop = 2   