# app.py
import streamlit as st
import pandas as pd
from decimal import Decimal
from db import init_db, list_products, create_product, update_product, delete_product, adjust_stock, place_order, list_orders, get_order
from db import session_scope, Product, Order, OrderItem
import db as db_module

st.set_page_config(page_title="E-commerce DB Manager", layout="wide")

# ---------- Custom CSS Theme ----------
st.markdown("""
    <style>
        body {
            background: linear-gradient(120deg, #89f7fe, #66a6ff);
        }
        .stApp {
            background-color: rgba(255,255,255,0.9);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        h1, h2, h3, h4 {
            color: #2c3e50;
        }
        .stSidebar {
            background: linear-gradient(180deg, #6a11cb, #2575fc);
        }
        .stButton>button {
            background-color: #6a11cb;
            color: white;
            border-radius: 8px;
            padding: 6px 16px;
        }
        .stButton>button:hover {
            background-color: #2575fc;
        }
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# initialize DB
init_db()

st.title("🌟 E-commerce Management System")

menu = st.sidebar.selectbox("Choose section", ["Products", "Orders", "Place Order", "Stock Adjust", "Order Reports"])

# ---------- Products ----------
if menu == "Products":
    st.header("📦 Product Management")
    products = list_products()
    df = pd.DataFrame([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": float(p.price),
        "stock": p.stock,
        "created_at": p.created_at
    } for p in products])
    st.subheader("Products table")
    st.dataframe(df, use_container_width=True)

    st.subheader("➕ Add new product")
    with st.form("add_product"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        stock = st.number_input("Stock", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product")
        if submitted:
            try:
                create_product(name=name, price=Decimal(str(price)), stock=int(stock), description=description)
                st.success("✅ Product added.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("✏️ Edit / Delete product")
    selected = st.selectbox("Select product", options=df['id'].tolist() if not df.empty else [])
    if selected:
        p = next((x for x in products if x.id == selected), None)
        if p:
            with st.form("edit_product"):
                new_name = st.text_input("Name", value=p.name)
                new_price = st.number_input("Price", min_value=0.0, value=float(p.price), format="%.2f")
                new_stock = st.number_input("Stock", min_value=0, value=int(p.stock), step=1)
                new_desc = st.text_area("Description", value=p.description if p.description else "")
                update_btn = st.form_submit_button("Update product")
                delete_btn = st.form_submit_button("Delete product")
                if update_btn:
                    try:
                        update_product(p.id, name=new_name, price=Decimal(str(new_price)), stock=int(new_stock), description=new_desc)
                        st.success("✅ Product updated.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                if delete_btn:
                    try:
                        delete_product(p.id)
                        st.success("🗑️ Product deleted.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ---------- Place Order ----------
elif menu == "Place Order":
    st.header("🛒 Place Order")
    products = list_products()
    if not products:
        st.info("No products. Add products first.")
    else:
        prod_df = pd.DataFrame([{"id": p.id, "name": p.name, "price": float(p.price), "stock": p.stock} for p in products])
        st.write("Available products")
        st.dataframe(prod_df, use_container_width=True)

        with st.form("order_form"):
            customer_name = st.text_input("Customer name")
            customer_email = st.text_input("Customer email")
            st.markdown("**Order items** (enter product id and qty rows)")
            items_raw = st.text_area("Format: product_id,qty (e.g. 1,2)")
            place = st.form_submit_button("Place Order")
            if place:
                try:
                    items = []
                    for line in items_raw.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        parts = [s.strip() for s in line.split(",")]
                        if len(parts) != 2:
                            raise ValueError(f"Bad line: {line}")
                        items.append({"product_id": int(parts[0]), "qty": int(parts[1])})
                    order_id = place_order(customer_name=customer_name, customer_email=customer_email, items=items)
                    st.success(f"🎉 Order placed. Order ID: {order_id}")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to place order: {e}")

# ---------- Orders ----------
elif menu == "Orders":
    st.header("📑 Orders")
    orders = list_orders()
    if not orders:
        st.info("No orders yet.")
    else:
        rows = []
        for o in orders:
            rows.append({"id": o.id, "customer": o.customer_name, "email": o.customer_email,
                         "total": float(o.total_amount), "status": o.status, "created_at": o.created_at})
        ord_df = pd.DataFrame(rows)
        st.dataframe(ord_df, use_container_width=True)
