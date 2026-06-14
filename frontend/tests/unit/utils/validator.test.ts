import { 
  isValidPhone, 
  isValidEmail, 
  escapeHtml, 
  stripHtml,
  isString,
  isNumber,
  isArray,
  isObject,
  isNil,
  isEmpty
} from '@/utils/validator'

describe('Validator Utilities', () => {
  describe('isValidPhone', () => {
    it('should return true for valid phone numbers', () => {
      expect(isValidPhone('13800138000')).toBe(true)
      expect(isValidPhone('15912345678')).toBe(true)
      expect(isValidPhone('18888888888')).toBe(true)
    })

    it('should return false for invalid phone numbers', () => {
      expect(isValidPhone('123456')).toBe(false)
      expect(isValidPhone('1380013800')).toBe(false)
      expect(isValidPhone('138001380000')).toBe(false)
      expect(isValidPhone('abc12345678')).toBe(false)
      expect(isValidPhone('')).toBe(false)
      expect(isValidPhone(null as any)).toBe(false)
      expect(isValidPhone(undefined as any)).toBe(false)
    })
  })

  describe('isValidEmail', () => {
    it('should return true for valid email addresses', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name@domain.co')).toBe(true)
      expect(isValidEmail('user+tag@example.org')).toBe(true)
    })

    it('should return false for invalid email addresses', () => {
      expect(isValidEmail('invalid-email')).toBe(false)
      expect(isValidEmail('@no-local-part.com')).toBe(false)
      expect(isValidEmail('no-at-sign.com')).toBe(false)
      expect(isValidEmail('no-domain@')).toBe(false)
      expect(isValidEmail('')).toBe(false)
      expect(isValidEmail(null as any)).toBe(false)
    })
  })

  describe('escapeHtml', () => {
    it('should escape HTML special characters', () => {
      const input = '<script>alert(1)</script>'
      const expected = '&lt;script&gt;alert(1)&lt;/script&gt;'
      expect(escapeHtml(input)).toBe(expected)
    })

    it('should handle quotes', () => {
      // Note: textContent does not escape quotes, they remain as-is
      expect(escapeHtml('"quoted"')).toBe('"quoted"')
      expect(escapeHtml("'single'")).toBe("'single'")
    })

    it('should handle non-string inputs', () => {
      expect(escapeHtml(null as any)).toBe(null)
      expect(escapeHtml(undefined as any)).toBe(undefined)
      expect(escapeHtml(123 as any)).toBe(123)
    })
  })

  describe('stripHtml', () => {
    it('should remove HTML tags', () => {
      expect(stripHtml('<p>Hello <b>World</b></p>')).toBe('Hello World')
    })

    it('should handle empty strings', () => {
      expect(stripHtml('')).toBe('')
    })

    it('should handle non-string inputs', () => {
      expect(stripHtml(null as any)).toBe(null)
      expect(stripHtml(undefined as any)).toBe(undefined)
    })

    it('should preserve whitespace when keepWhitespace is true', () => {
      expect(stripHtml('<div>Line 1\nLine 2</div>')).toBe('Line 1\nLine 2')
    })

    it('should collapse whitespace when keepWhitespace is false', () => {
      expect(stripHtml('<div>Line 1\nLine 2</div>', false)).toBe('Line 1 Line 2')
    })
  })

  describe('Type Guards', () => {
    describe('isString', () => {
      it('should return true for strings', () => {
        expect(isString('hello')).toBe(true)
        expect(isString('')).toBe(true)
      })

      it('should return false for non-strings', () => {
        expect(isString(123)).toBe(false)
        expect(isString(null)).toBe(false)
        expect(isString(undefined)).toBe(false)
        expect(isString({})).toBe(false)
        expect(isString([])).toBe(false)
      })
    })

    describe('isNumber', () => {
      it('should return true for numbers', () => {
        expect(isNumber(42)).toBe(true)
        expect(isNumber(0)).toBe(true)
        expect(isNumber(-1)).toBe(true)
        expect(isNumber(3.14)).toBe(true)
      })

      it('should return false for non-numbers', () => {
        expect(isNumber('42')).toBe(false)
        expect(isNumber(null)).toBe(false)
        expect(isNumber(undefined)).toBe(false)
        expect(isNumber(NaN)).toBe(false)
      })
    })

    describe('isArray', () => {
      it('should return true for arrays', () => {
        expect(isArray([])).toBe(true)
        expect(isArray([1, 2, 3])).toBe(true)
        expect(isArray(['a', 'b'])).toBe(true)
      })

      it('should return false for non-arrays', () => {
        expect(isArray({})).toBe(false)
        expect(isArray('array')).toBe(false)
        expect(isArray(null)).toBe(false)
        expect(isArray(undefined)).toBe(false)
      })
    })

    describe('isObject', () => {
      it('should return true for objects', () => {
        expect(isObject({})).toBe(true)
        expect(isObject({ key: 'value' })).toBe(true)
      })

      it('should return false for non-objects', () => {
        expect(isObject([])).toBe(false)
        expect(isObject('object')).toBe(false)
        expect(isObject(null)).toBe(false)
        expect(isObject(undefined)).toBe(false)
        expect(isObject(42)).toBe(false)
      })
    })

    describe('isNil', () => {
      it('should return true for null or undefined', () => {
        expect(isNil(null)).toBe(true)
        expect(isNil(undefined)).toBe(true)
      })

      it('should return false for other values', () => {
        expect(isNil('')).toBe(false)
        expect(isNil(0)).toBe(false)
        expect(isNil({})).toBe(false)
        expect(isNil([])).toBe(false)
      })
    })

    describe('isEmpty', () => {
      it('should return true for empty values', () => {
        expect(isEmpty(null)).toBe(true)
        expect(isEmpty(undefined)).toBe(true)
        expect(isEmpty('')).toBe(true)
        expect(isEmpty('   ')).toBe(true)
        expect(isEmpty([])).toBe(true)
        expect(isEmpty({})).toBe(true)
      })

      it('should return false for non-empty values', () => {
        expect(isEmpty('hello')).toBe(false)
        expect(isEmpty([1, 2, 3])).toBe(false)
        expect(isEmpty({ key: 'value' })).toBe(false)
        expect(isEmpty(0)).toBe(false)
        expect(isEmpty(false)).toBe(false)
      })
    })
  })
})
