import argparse
import logging
from app.models.trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Train FraudShield Models")
    parser.add_argument("--csv_path", type=str, default="historical_transactions.csv", help="Path to the dataset CSV")
    parser.add_argument("--target", type=str, default="Fraud_Label", help="Target column")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test set size")
    args = parser.parse_args()

    trainer = ModelTrainer(csv_path=args.csv_path, target=args.target, test_size=args.test_size)
    results, best_name = trainer.train_and_evaluate()
    
    print("\n--- Training Results ---")
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        for k, v in metrics.items():
            print(f"  {k}: {v:.4f}")
            
    print(f"\nBest Model: {best_name}")

if __name__ == "__main__":
    main()
