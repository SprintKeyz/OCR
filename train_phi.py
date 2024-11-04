import util.get_image as get_image
import csv
import os
import sys
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForCausalLM, AutoProcessor
import argparse

class Phi3VisionModel:
    def __init__(self, model_id="microsoft/Phi-3-vision-128k-instruct", device="cuda"):
        self.model_id = model_id
        self.device = device
        self.model = self.load_model()
        self.processor = self.load_processor()
        torch.cuda.empty_cache()
        
    def load_model(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="cuda:0",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            _attn_implementation="flash_attention_2"
        )
        model = torch.compile(model)
        return model.to(self.device)
    
    def load_processor(self):
        return AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
    
    def fine_tune(self, dataset, batch_size=8, num_epochs=3, learning_rate=5e-5):
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        self.model.train()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

        for epoch in range(num_epochs):
            for step, (images, prompts, labels) in enumerate(dataloader):
                images = images.to(self.device)
                labels = labels.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(images, labels=labels)
                loss = outputs.loss
                
                print(f"Epoch {epoch}, Step {step}, Loss: {loss.item()}")
                
                loss.backward()
                optimizer.step()
        
        self.save_model()
    
    def save_model(self, save_path='fine_tuned_model'):
        self.model.save_pretrained(save_path)
        self.processor.save_pretrained(save_path)

class HandwritingDataset(Dataset):
    def __init__(self, data_dir, processor):
        self.data_dir = data_dir
        self.processor = processor
        self.image_paths = []
        self.labels = []
        self.prompts = []
        self.load_data()

    def load_data(self):
        with open(os.path.join(self.data_dir, 'Tracking.csv'), 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                index = int(row[0])  # student index
                label = ','.join(filter(None, [row[2], row[3]]))  # Concatenate answers, ignore None
                image_path = os.path.join(self.data_dir, f's{index:05d}.pdf.jpg')  # Formatting to match file names
                self.image_paths.append(image_path)
                self.labels.append(label)
                self.prompts.append("Extract the answers labeled 'a:' and 'b:' from the document. Only return the answers in a comma-separated format ((WITHOUT SPACES)) with (NO extra text).")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = get_image.load_image(self.image_paths[idx])  # Implement this function in get_image module
        label = self.labels[idx]
        prompt = self.prompts[idx]

        # Prepare inputs for the model
        inputs = self.processor(
            [image],  # Make sure this is a list
            prompt, 
            return_tensors="pt", 
            padding=True
        )
        
        # Returning image tensors and labels
        return inputs['pixel_values'].squeeze(0), inputs['input_ids'].squeeze(0), label  # Adjust based on processor output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fine-tune Phi-3 Vision Model.')
    parser.add_argument('-d', '--data', type=str, required=True, help='Data directory')
    parser.add_argument('-b', '--batch_size', type=int, default=8, help='Batch size for training')
    parser.add_argument('-e', '--epochs', type=int, default=3, help='Number of training epochs')
    parser.add_argument('-lr', '--learning_rate', type=float, default=5e-5, help='Learning rate for training')

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print('Data directory does not exist.')
        sys.exit()

    # Initialize model and dataset
    phi_model = Phi3VisionModel()
    dataset = HandwritingDataset(args.data, phi_model.processor)
    
    # Fine-tune the model
    phi_model.fine_tune(dataset, batch_size=args.batch_size, num_epochs=args.epochs, learning_rate=args.learning_rate)
