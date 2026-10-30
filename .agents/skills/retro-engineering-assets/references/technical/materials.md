## Finding and using materials

Start with general Google results without domain or site: restrictions, also inspecting Google Images and video results. Use domain-specific queries after broad searching to refine a discovered source. Explore archives, museum collections, historical and creator sites, and YouTube; stock libraries are not the only source category. Record inspected non-stock results and rejection reasons: style fit, depicted content, terms, and accessibility. Do not claim “searched all of Google” after only site:pexels.com queries.

Google finds original pages; it does not grant permission. Search in Russian and English, using local names for places where relevant. Start with the exact place/object, then contextual queries. Save queries, inspected links, and rejection reasons in assets/search_log.json; group repeated queries by location and era.

Possible sources: Wikimedia Commons, open museum collections, Library of Congress Free to Use and Reuse, Internet Archive with verified status for the specific item, and creator materials with explicit permission. Found videos and photos may depict archival events, modern locations, museum objects, documents, people, or mechanisms. Verify era, identity, and context under the chosen channel's rules. Modern footage and reconstructions are not archival recordings of the described event.

In this workflow, interpret “license-free” as material whose intended use is confirmed: public domain, CC0, an applicable open license, or author permission. For each file, record source, author, exact terms, a terms link, and required attribution. If terms are unknown, find another version rather than use it merely because it is downloadable. Comply with additional license conditions; Creative Commons variants are not interchangeable. Add attribution to descriptions in every requested language.

Research YouTube with yt-dlp without downloading (title, description, duration, license). For reuse, choose material with verified permission such as applicable CC BY or author authorization; the standard YouTube license alone does not grant it. A description label is evidence to verify, not a guarantee of the uploader's rights. Prefer an original archival file to a YouTube copy when available. Cutting a short segment does not automatically make it free to use.

For permitted video, yt-dlp supports time-range selection through --download-sections with a range such as *00:01:20-00:01:28 and FFmpeg. Inspect the original video and select a segment before downloading, then verify beginning/end. If extraction is insufficiently precise, trim the local file accurately with re-encoding. Do not download entire channels or every found video for one shot. Avoid third-party titles/logos by selecting suitable sources, not by hiding required attribution.

## Generating missing visuals

Built-in image_gen under the imagegen skill is the primary GPT image-generation route; it needs no separate API key. Do not switch to CLI/API without a user request. Within requested video production, generating missing scenes is part of the defined workflow.

Each brief specifies action, place, era, costume, objects, emotional emphasis, lighting, and 16:9 composition. The image must serve an exact phrase. Follow the selected channel's approved visual profile rather than substituting another. Harmonize found and generated shots in mood, scale, and color; avoid repeating a composition. Do not pass generation off as found archival material. Save prompt and generated status in the registry; omit text unless the scene requires it. Apply exact captions separately when needed.

Registry schema (path relative to manifest.json):

```json
{
  "assets": [
    {
      "id": "asset_001",
      "kind": "image",
      "path": "downloaded/asset_001.jpg",
      "source_url": "URL of the original page for this specific asset",
      "author": "Author or organization",
      "rights_basis": "Exact usage terms",
      "rights_url": "URL of terms or permission evidence",
      "attribution": "Required credit",
      "usage_status": "approved",
      "historical_role": "Modern location footage / object / reconstruction"
    }
  ]
}
```

Set usage_status=approved only after checking the asset and terms, not in bulk for search results. For generated material, record kind=image, path, a source_url such as generated://scene_001, prompt, generation method, and rights_basis stating that it is an original generation within the project. The renderer checks for a registry entry but does not independently establish the file's legal status.

Sources: https://support.google.com/youtube/answer/2797468 ; https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia ; https://github.com/yt-dlp/yt-dlp#download-options
