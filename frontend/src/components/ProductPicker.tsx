import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { Formik } from "formik";

import { Product, getProduct } from "../api";

export interface Props {
  store: string;
  onAddProduct?: (ean: string) => Promise<void>;
}

export default function ProductPicker({ store, onAddProduct }: Props) {
  const [product, setProduct] = React.useState<Product | null>(null);

  return (
    <div className="product-picker">
      <Formik
        initialValues={{ ean: "" }}
        validate={async (values) => {
          const errors: Record<string, string> = {};
          if (!/^[0-9]{13}$/.test(values.ean)) {
            errors.ean = "Invalid EAN";
          } else {
            await getProduct(store, values.ean)
              .then(setProduct)
              .catch((e) => {
                errors.ean = e.message;
              });
          }
          return errors;
        }}
        onSubmit={(
          values,
          { resetForm, setFieldError, setSubmitting }
        ) => {
          if (onAddProduct) {
            onAddProduct(values.ean)
              .then(() => resetForm())
              .catch((e) => setFieldError("ean", e.message))
              .finally(() => setSubmitting(false));
          }
        }}
      >
        {({
          handleSubmit,
          handleChange,
          handleBlur,
          values,
          errors,
          touched,
          isValid,
          isSubmitting,
        }) => (
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col>
                <Form.Control
                  name="ean"
                  placeholder="EAN Code"
                  value={values.ean}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  isValid={!errors.ean && touched.ean}
                  isInvalid={Boolean(errors.ean && touched.ean)}
                />
                {errors.ean && (
                  <Form.Control.Feedback type="invalid">
                    {errors.ean}
                  </Form.Control.Feedback>
                )}
                {product && (
                  <Form.Control.Feedback>{product.name}</Form.Control.Feedback>
                )}
              </Col>
              <Col>
                <Button type="submit" disabled={!isValid || isSubmitting}>
                  Add product
                </Button>
              </Col>
            </Row>
          </Form>
        )}
      </Formik>
    </div>
  );
}
