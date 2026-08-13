import { ProductPageClient } from "./ProductPageClient";

type ProductPageProps = {
  params: { id: string };
};

export default function ProductPage({ params }: ProductPageProps) {
  return <ProductPageClient productId={Number(params.id)} />;
}
