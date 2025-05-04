import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
from flask import Blueprint, request, jsonify
from src.scraper import scrape_gsmarena # Import the async scraper function

gsmarena_bp = Blueprint('gsmarena', __name__)

@gsmarena_bp.route('/search', methods=['GET'])
def search_phone():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        # Run the async function in a way Flask can handle
        # asyncio.run() creates a new event loop for each request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scrape_gsmarena(query))
        loop.close()

        if "error" in result:
            # Return specific error codes based on the scraper's output if needed
            # For now, returning 500 for any scraping error
            return jsonify(result), 500
        return jsonify(result)
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"Error in /search route: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

