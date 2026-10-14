// Geocoded names are long ("Charminar, Ghansi Bazaar, Hyderabad, ..., India").
// Show the first three comma-separated parts; callers keep the full name as a tooltip.
export function shortPlaceName(name) {
  return name
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, 3)
    .join(', ')
}
