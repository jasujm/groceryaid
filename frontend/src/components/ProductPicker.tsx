import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import { Formik } from "formik";

export interface Props {
  onAddProduct?: (ean: string) => Promise<void>;
}

export default function ProductPicker({ onAddProduct }: Props) {
  return (
    <div className="product-picker">
      <Formik
        initialValues={{ ean: "" }}
        validate={(values) => {
          const errors: Record<string, string> = {};
          if (!/[0-9]{13}/i.test(values.ean)) {
            errors.ean = "Invalid EAN";
          }
          return errors;
        }}
        onSubmit={(
          values,
          { setFieldValue, setFieldTouched, setFieldError, setSubmitting }
        ) => {
          if (onAddProduct) {
            onAddProduct(values.ean)
              .then(() => {
                setFieldValue("ean", "");
                setFieldTouched("ean", false);
              })
              .catch((e) => {
                setFieldError("ean", e.message);
              })
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
                <Form.Control.Feedback type="invalid">
                  {errors.ean}
                </Form.Control.Feedback>
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
