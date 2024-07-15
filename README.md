
---

# AWS EC2 Script

Este script permite gestionar instancias de Amazon EC2 mediante la línea de comandos. Puedes crear, eliminar y listar instancias EC2 utilizando varios argumentos.

## Argumentos

El script acepta los siguientes argumentos:

### Crear una instancia EC2

- `-c`, `--create`: Indica que se debe crear una nueva instancia EC2.
- `-n`, `--name`: Nombre de la instancia que se creará.
- `-a`, `--ami-id`: ID de la imagen EC2.
- `-k`, `--key-name`: Nombre del Key Pair para el acceso SSH.
- `-t`, `--type-instance`: Tipo de instancia. Si no se especifica, el valor predeterminado será `t2.micro`.

### Eliminar una instancia EC2

- `-d`, `--destroy`: Indica que se debe terminar una instancia EC2.
- `-i`, `--instance-id`: ID de la instancia a eliminar.

### Listar instancias EC2

- `-l`, `--list`: Muestra el listado de las instancias existentes.

## Uso

### Crear una instancia

Para crear una instancia EC2, utiliza el siguiente comando:

```sh
python main.py -c -n "test-mv" -a "ami-0b72821e2f351e396" -k "test-key"
```

### Eliminar una instancia

Para eliminar una instancia EC2, utiliza el siguiente comando:

```sh
python main.py -d -i "id-de-la-instancia"
```

### Listar instancias

Para obtener un listado de las instancias creadas, utiliza el siguiente comando:

```sh
python main.py -l
```

## Ejemplos

### Crear una instancia

```sh
python main.py -c -n "mi-instancia" -a "ami-0b72821e2f351e396" -k "mi-key-pair"
```

### Eliminar una instancia

```sh
python main.py -d -i "i-1234567890abcdef0"
```

### Listar instancias

```sh
python main.py -l
```
---