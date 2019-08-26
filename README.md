# Simulator

## Description

A simple Python GUI application, which has 4 movable cylinders and motors.

You can control the cylinders and motors with a PLC program running on TwinCAT 3. The simulator and PLC program are communicating by using the Automation Device Specification (ADS) protocol.

![Simulator UI](https://github.com/hhaka/simulator/blob/master/ui.png "Simulator UI")

## Dependencies

The simulator uses [pyads](https://pypi.org/project/pyads/) and [PyQy5](https://pypi.org/project/PyQt5/) packages. You can install them with the pip:

```
pip install pyads PyQt5
```

## TwinCAT I/O Configuration

Input variables

```
VAR_INPUT
	iCyl1minus AT %IX0.0: BOOL;
	iCyl1plus AT %IX0.1: BOOL;
	iCyl2minus AT %IX0.3: BOOL;
	iCyl2plus AT %IX0.4: BOOL;
	iCyl3minus AT %IX1.0: BOOL;
	iCyl3plus AT %IX1.1: BOOL;
	iCyl4minus AT %IX1.3: BOOL;
	iCyl4plus AT %IX1.4: BOOL;
	iMot1running AT %IX0.2: BOOL;
	iMot2running AT %IX0.5: BOOL;
	iMot3running AT %IX1.2: BOOL;
	iMot4running AT %IX1.5: BOOL;
END_VAR
```

Output variables

```
VAR_OUTPUT
	qCyl1toMinus AT %QX0.0: BOOL;
	qCyl1toPlus AT %QX0.1: BOOL;
	qCyl2toMinus AT %QX0.3: BOOL;
	qCyl2toPlus AT %QX0.4: BOOL;
	qCyl3toMinus AT %QX1.0: BOOL;
	qCyl3toPlus AT %QX1.1: BOOL;
	qCyl4toMinus AT %QX1.3: BOOL;
	qCyl4toPlus AT %QX1.4: BOOL;
	qMot1start AT %QX0.2: BOOL;
	qMot2start AT %QX0.5: BOOL;
	qMot3start AT %QX1.2: BOOL;
	qMot4start AT %QX1.5: BOOL;
END_VAR
```

## Usage

1. Start the TwinCAT 3 project in Run Mode
1. Start the simulator

```
python simulator.py
```

## Troubleshooting

If the simulator fails to connect with the TwinCAT 3, copy the NetId address from TwinCAT 3 to the simulator.

1. Double click the **Routes** on **Solution Explorer** window
1. Open the **NetId Management** tab
1. Copy the address on the **Local NetId** text box
1. Open the **Settings** tab on the simulator and paste the address to the **AMS Net Id** text box
1. Click **Update values** button

## Additional Information

This application has been made as a part of the "Automation in Network" project.
