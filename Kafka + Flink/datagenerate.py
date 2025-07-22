import json
import random
import time
import uuid

class StockSimulator:
    """
    A stateful simulator that mimics a real-world inventory system by generating
    distinct business events (orders and stock receipts) and managing an internal
    inventory state.
    """
    def __init__(self, num_products=10):
        # Configuration
        self.products = {f"PROD-{i:03d}": {"reorder_point": 10, "max_stock": 100} for i in range(1, num_products + 1)}
        self.inventory = {p: random.randint(20, 80) for p in self.products.keys()}
        print("--- Initial Inventory State ---")
        print(self.inventory)
        print("--------------------------------")

    def _generate_new_order(self):
        """
        Generates a new customer order event. This represents DEMAND.
        It will only sell products that are currently in stock.
        """
        # Find products that are available to be sold
        available_products = [p for p, stock in self.inventory.items() if stock > 0]
        if not available_products:
            return None # No stock anywhere, can't generate an order

        product_id = random.choice(available_products)
        current_stock = self.inventory[product_id]
        
        # Order quantity is between 1 and a small fraction of available stock, but at least 1
        quantity_ordered = random.randint(1, max(1, min(5, current_stock)))
        
        # Update internal state
        self.inventory[product_id] -= quantity_ordered

        event = {
            "metadata": {"event_type": "new_order", "target_topic": "orders"},
            "payload": {
                "order_id": str(uuid.uuid4()),
                "product_id": product_id,
                "quantity": quantity_ordered,
                "customer_id": f"CUST-{random.randint(100, 999)}",
                "order_value": round(random.uniform(5.0, 100.0) * quantity_ordered, 2),
                "order_timestamp": time.time()
            }
        }
        return event

    def _generate_stock_received(self, product_id):
        """
        Generates a stock receipt event. This represents SUPPLY.
        It's triggered when stock falls below the reorder point.
        """
        product_info = self.products[product_id]
        restock_quantity = random.randint(product_info['max_stock'] // 2, product_info['max_stock'])

        # Update internal state
        self.inventory[product_id] += restock_quantity
        
        event = {
            "metadata": {"event_type": "stock_received", "target_topic": "inventory_movements"},
            "payload": {
                "shipment_id": str(uuid.uuid4()),
                "product_id": product_id,
                "quantity": restock_quantity,
                "source": f"SUPPLIER-{random.choice(['A', 'B', 'C'])}",
                "received_timestamp": time.time()
            }
        }
        return event

    def run_simulation(self):
        """
        The main simulation loop. It continuously generates events based on the
        current state of the inventory.
        """
        print("Starting Advanced Event Simulator... Press Ctrl+C to stop.")
        
        while True:
            # --- Logic to check if a restock is needed ---
            products_to_restock = [
                p for p, stock in self.inventory.items() 
                if stock < self.products[p]['reorder_point']
            ]
            
            # Prioritize restocking if needed
            if products_to_restock and random.random() < 0.3: # Don't always restock immediately
                product_to_restock = random.choice(products_to_restock)
                event = self._generate_stock_received(product_to_restock)
                print(f"[LOG] Restocking {product_to_restock}. Current stock: {self.inventory[product_to_restock]}")
            else:
                # Otherwise, generate a customer order
                event = self._generate_new_order()

            if event:
                # Print the full event as a JSON string to stdout
                print(json.dumps(event))
                
                # Flush to ensure it's sent immediately
                import sys
                sys.stdout.flush()

            # Wait a bit before the next event
            time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    simulator = StockSimulator(num_products=5)
    try:
        simulator.run_simulation()
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")
        print("\n--- Final Inventory State ---")
        print(simulator.inventory)
        print("-----------------------------")