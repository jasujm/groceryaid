export function calculateCheckDigit(eanPrefix: string) {
  const checksum =
    eanPrefix
      .split("")
      .map((c, index) => (index % 2 === 0 ? 1 : 3) * Number(c))
      .reduce((a, b) => a + b, 0) % 10;
  if (checksum === 0) {
    return "0";
  }
  return String(10 - checksum);
}

export function isValidEan(ean: string) {
  return (
    /^[0-9]{13}$/.test(ean) &&
    calculateCheckDigit(ean.slice(0, 12)) === ean.slice(12)
  );
}

export function isVariablePriceEan(ean: string) {
  return ean.startsWith("2");
}
