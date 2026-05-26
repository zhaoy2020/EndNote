from loguru import logger 
from argparse import ArgumentParser
from tqdm import tqdm 
from pathlib import Path

import numpy as np
import pandas as pd


class JournalTermMaker:
    def __init__(self, match_table: pd.DataFrame):
        self.match_table = self.read_file(match_table)
        self.raw_match_table = self.match_table.copy()

    def read_file(self, file_name: str):
        file_name = Path(file_name)
        if file_name.suffix == '.xlsx':
            return pd.read_excel(file_name)
        elif file_name.suffix == '.csv':
            return pd.read_csv(file_name)
        elif file_name.suffix == '.txt':
            return pd.read_csv(file_name, sep='\t')
        else:
            raise ValueError("Unsupported file format. Please provide an Excel (.xlsx), CSV (.csv), or TXT (.txt) file.")

    def add(self, full_name: str, iso_abbreviation: str, jcr_abbreviation: str):
        if full_name.upper() not in self.match_table['Full Name'].str.upper().values:
            new_term = pd.DataFrame({
                'Full Name': [full_name],
                'ISO Abbreviation': [iso_abbreviation],
                'JCR Abbreviation': [jcr_abbreviation],
            })
            self.match_table = pd.concat([self.match_table, new_term], ignore_index=True)
            logger.info(f"Added term: {full_name} | {iso_abbreviation} | {jcr_abbreviation}")
        else:
            logger.warning(f"Term '{full_name}' already exists in the match table.")

        return None
    
    def add_from_file(self, file_path: str):
        self.query_terms_table = self.read_file(file_path)
        # for _, row in tqdm(self.query_terms_table.iterrows(), total=self.query_terms_table.shape[0], desc="Adding terms", position=0, leave=True):
        for _, row in self.query_terms_table.iterrows():
            self.add(row['Full Name'], row['ISO Abbreviation'], row['JCR Abbreviation'])

        return None
    
    def save(self, output_file: str):
        output_file = Path(output_file)
        if output_file.suffix == '.xlsx':
            self.match_table.to_excel(output_file, index=False)
        elif output_file.suffix == '.csv':
            self.match_table.to_csv(output_file, index=False)
        elif output_file.suffix == '.txt':
            self.match_table.to_csv(output_file, index=False, sep='\t')
        else:
            raise ValueError("Unsupported file format. Please provide an Excel (.xlsx), CSV (.csv), or TXT (.txt) file.")


def parse_arguments():
    parser = ArgumentParser(description="Journal Term Maker for EndNote")
    parser.add_argument('--match_table', type=str, required=False, default='match_table.csv', help='Path to the match table CSV file')
    parser.add_argument('--add_term', nargs=3, metavar=('FULL_NAME', 'ISO_ABBREVIATION', 'JCR_ABBREVIATION'), help='Add a new term to the match table')
    parser.add_argument('--add_from_file', type=str, required=False, default= 'new_terms.csv', help='Path to the input file containing terms to add (optional)')
    parser.add_argument('--output', type=str, default='updated_match_table.csv', help='Path to save the updated match table csv file')
    return parser.parse_args()


def main():
    args = parse_arguments()
    term_maker = JournalTermMaker(args.match_table)

    if args.add_term:
        full_name, iso_abbreviation, jcr_abbreviation = args.add_term
        term_maker.add(full_name, iso_abbreviation, jcr_abbreviation)

    if args.add_from_file:
        term_maker.add_from_file(args.add_from_file)

    # Save the updated match table to a CSV file
    if args.output:
        logger.info(f'Total | Query | Added: {term_maker.match_table.shape[0]} | {term_maker.query_terms_table.shape[0]} | {term_maker.match_table.shape[0] - term_maker.raw_match_table.shape[0]}')
        logger.info(f'Saving updated match table to {args.output}')
        term_maker.save(args.output)


if __name__ == "__main__":
    main()