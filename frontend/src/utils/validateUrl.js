/**
 * Validates a given URL string against a regular expression pattern.
 *
 * The function checks if the input string is a well-formed URL.
 *
 * Returns:
 *   Boolean: True if the URL is valid according to the regular expression, False otherwise.
 *
 * Usage example:
 *   validateUrl("https://www.example.com"); // Returns true
 *   validateUrl("ftp://example.com"); // Returns false, as the protocol is not HTTP or HTTPS
 */
const validateUrl = (url) => {
    const pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
      '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
      '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
      '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
    return !!pattern.test(url);
  }

  export default validateUrl;
