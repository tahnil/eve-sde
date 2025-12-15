# eve-sde
Provides data from the EVE Online SDE in easily digestible up-to-date JSON files

## Available Data

### `data/ores.json`
Contains ore and mineral data with reprocessing information:
- All published ores (regular and compressed)
- Minerals (Tritanium, Pyerite, Mexallon, etc.)
- Reprocessing yields for ores

### `data/items.json`
Contains volume data for all published items in EVE Online:
- Item ID, name, and volume
- Group and category information
- Useful for manufacturing, logistics, and inventory calculations

## Updates

Data is automatically updated weekly (every Sunday) via GitHub Actions, pulling the latest SDE from CCP's servers.
