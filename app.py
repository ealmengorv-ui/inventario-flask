from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "inventario-clave"


# LISTADO Y BÚSQUEDA
@app.route("/")
def index():
    busqueda = request.args.get("q", "").strip()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if busqueda:
        termino = f"%{busqueda}%"

        cur.execute("""
            SELECT * FROM productos
            WHERE codigo ILIKE %s
               OR nombre ILIKE %s
               OR categoria ILIKE %s
            ORDER BY id DESC
        """, (termino, termino, termino))
    else:
        cur.execute("""
            SELECT * FROM productos
            ORDER BY id DESC
        """)

    productos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        productos=productos,
        busqueda=busqueda
    )


# REGISTRAR
@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        nombre = request.form["nombre"].strip()
        categoria = request.form["categoria"].strip()
        precio = request.form["precio"].strip()
        existencia = request.form["existencia"].strip()
        activo = "activo" in request.form

        if not codigo or not nombre or not categoria or not precio or not existencia:
            flash("Todos los campos obligatorios deben estar completos.", "error")
            return render_template("form.html", producto=None)

        try:
            precio = float(precio)
            existencia = int(existencia)

            if precio <= 0:
                flash("El precio debe ser mayor que cero.", "error")
                return render_template("form.html", producto=None)

            if existencia < 0:
                flash("La existencia no puede ser negativa.", "error")
                return render_template("form.html", producto=None)

        except ValueError:
            flash("Precio o existencia no tienen un valor válido.", "error")
            return render_template("form.html", producto=None)

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO productos
                (codigo, nombre, categoria, precio, existencia, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                codigo,
                nombre,
                categoria,
                precio,
                existencia,
                activo
            ))

            conn.commit()
            cur.close()
            conn.close()

            flash("Producto registrado correctamente.", "exito")

        except psycopg2.IntegrityError:
            flash("El código del producto ya existe.", "error")

        return redirect(url_for("index"))

    return render_template("form.html", producto=None)


# EDITAR
@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        nombre = request.form["nombre"].strip()
        categoria = request.form["categoria"].strip()
        precio = request.form["precio"].strip()
        existencia = request.form["existencia"].strip()
        activo = "activo" in request.form

        if not codigo or not nombre or not categoria or not precio or not existencia:
            flash("Todos los campos obligatorios deben estar completos.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("editar_producto", id=id))

        try:
            precio = float(precio)
            existencia = int(existencia)

            if precio <= 0:
                flash("El precio debe ser mayor que cero.", "error")
                cur.close()
                conn.close()
                return redirect(url_for("editar_producto", id=id))

            if existencia < 0:
                flash("La existencia no puede ser negativa.", "error")
                cur.close()
                conn.close()
                return redirect(url_for("editar_producto", id=id))

        except ValueError:
            flash("Precio o existencia no tienen un valor válido.", "error")
            cur.close()
            conn.close()
            return redirect(url_for("editar_producto", id=id))

        try:
            cur.execute("""
                UPDATE productos
                SET codigo=%s,
                    nombre=%s,
                    categoria=%s,
                    precio=%s,
                    existencia=%s,
                    activo=%s
                WHERE id=%s
            """, (
                codigo,
                nombre,
                categoria,
                precio,
                existencia,
                activo,
                id
            ))

            conn.commit()

        except psycopg2.IntegrityError:
            conn.rollback()
            cur.close()
            conn.close()

            flash("El código del producto ya pertenece a otro producto.", "error")
            return redirect(url_for("editar_producto", id=id))

        cur.close()
        conn.close()

        flash("Producto actualizado correctamente.", "exito")
        return redirect(url_for("index"))

    cur.execute(
        "SELECT * FROM productos WHERE id=%s",
        (id,)
    )

    producto = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "form.html",
        producto=producto
    )


# ELIMINAR
@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM productos WHERE id=%s",
        (id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    flash("Producto eliminado correctamente.", "exito")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)