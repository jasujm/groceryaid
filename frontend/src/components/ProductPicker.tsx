import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import InputGroup from "react-bootstrap/InputGroup";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { UpcScan, PlusLg } from "react-bootstrap-icons";
import { useFormik } from "formik";

import { Product, getProduct } from "../api";
import { isValidEan } from "../ean";

import BarcodeScanner from "./BarcodeScanner";

export interface Props {
  store: string;
  onAddProduct?: (ean: string) => Promise<void>;
}

export default function ProductPicker({ store, onAddProduct }: Props) {
  const [product, setProduct] = React.useState<Product | null>(null);
  const [scanning, setScanning] = React.useState(false);
  const {
    handleSubmit,
    handleChange,
    handleBlur,
    values,
    errors,
    touched,
    isValid,
    isSubmitting,
    setValues,
  } = useFormik({
    initialValues: { ean: "" },
    validate: async (values) => {
      const errors: Record<string, string> = {};
      if (!isValidEan(values.ean)) {
        errors.ean = "Invalid EAN";
      } else {
        await getProduct(store, values.ean)
          .then(setProduct)
          .catch((e) => (errors.ean = e.message));
      }
      return errors;
    },
    onSubmit: (values, { resetForm, setFieldError, setSubmitting }) => {
      if (onAddProduct) {
        onAddProduct(values.ean)
          .then(() => resetForm())
          .catch((e) => setFieldError("ean", e.message))
          .finally(() => setSubmitting(false));
      }
    },
  });

  function startScanning() {
    setScanning(true);
  }

  function stopScanning() {
    setScanning(false);
  }

  function onScanBarcode(ean: string) {
    setValues({ ean });
    stopScanning();
  }

  return (
    <Form className="product-picker" onSubmit={handleSubmit}>
      <Modal show={scanning} onHide={stopScanning}>
        <Modal.Header closeButton>
          <Modal.Title>Scan barcode</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <BarcodeScanner onScanBarcode={onScanBarcode} />
        </Modal.Body>
      </Modal>
      <Row>
        <Col xs={10}>
          <InputGroup>
            <Button
              variant="secondary"
              onClick={startScanning}
              aria-label="Scan barcode"
            >
              <UpcScan />
            </Button>
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
          </InputGroup>
        </Col>
        <Col xs={2}>
          <Button
            type="submit"
            disabled={!isValid || isSubmitting}
            aria-label="Add product"
          >
            <PlusLg />
          </Button>
        </Col>
      </Row>
    </Form>
  );
}
